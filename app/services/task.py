import math
import json
import os.path
import re
from os import path

from loguru import logger

from app.config import config
from app.models import const
from app.models.schema import VideoConcatMode, VideoParams
from app.services import llm, material, one_shot, subtitle, video, voice
from app.services import state as sm
from app.utils import utils


def _claim_once(params, stage: str):
    guard = getattr(params, "_one_shot_guard", None)
    if guard:
        guard.claim(stage)


def generate_script(task_id, params):
    logger.info("\n\n## generating video script")
    video_script = params.video_script.strip()
    if not video_script:
        video_script = llm.generate_script(
            video_subject=params.video_subject,
            language=params.video_language,
            paragraph_number=params.paragraph_number,
        )
    else:
        logger.debug(f"video script: \n{video_script}")

    if not video_script:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error("failed to generate video script.")
        return None

    return video_script


def generate_terms(task_id, params, video_script):
    logger.info("\n\n## generating video terms")
    video_terms = params.video_terms
    if not video_terms:
        video_terms = llm.generate_terms(
            video_subject=params.video_subject, video_script=video_script, amount=5
        )
        # llm.generate_terms returns the error message as a plain string on failure;
        # without this guard the string gets iterated character by character downstream
        if isinstance(video_terms, str) or not video_terms:
            logger.warning(
                f"term generation failed ({str(video_terms)[:80]}), falling back to video subject"
            )
            video_terms = [params.video_subject]
    else:
        if isinstance(video_terms, str):
            video_terms = [term.strip() for term in re.split(r"[,，]", video_terms)]
        elif isinstance(video_terms, list):
            video_terms = [term.strip() for term in video_terms]
        else:
            raise ValueError("video_terms must be a string or a list of strings.")

        logger.debug(f"video terms: {utils.to_json(video_terms)}")

    if not video_terms:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error("failed to generate video terms.")
        return None

    return video_terms


def save_script_data(task_id, video_script, video_terms, params):
    script_file = path.join(utils.task_dir(task_id), "script.json")
    params_data = (
        params.model_dump(mode="json")
        if hasattr(params, "model_dump")
        else params.dict()
        if hasattr(params, "dict")
        else params
    )
    script_data = {
        "script": video_script,
        "search_terms": video_terms,
        # Persist only declared request fields. Runtime-only objects such as the
        # one-shot guard contain locks/file handles and must never enter JSON.
        "params": params_data,
    }

    temp_file = script_file + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, script_file)


def generate_audio(task_id, params, video_script):
    logger.info("\n\n## generating audio")
    audio_file = path.join(utils.task_dir(task_id), "audio.mp3")
    _claim_once(params, "voice_generation")
    attempts = 1 if one_shot.is_enabled(params) else 3
    with voice.attempt_limit(attempts):
        sub_maker = voice.tts(
            text=video_script,
            voice_name=voice.parse_voice_name(params.voice_name),
            voice_rate=params.voice_rate,
            voice_file=audio_file,
            voice_volume=params.voice_volume,
        )
    if sub_maker is None:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error(
            """failed to generate audio:
1. check if the language of the voice matches the language of the video script.
2. check if the network is available. If you are in China, it is recommended to use a VPN and enable the global traffic mode.
        """.strip()
        )
        return None, None, None

    # Get the actual audio file path (might be .wav if MP3 conversion failed)
    actual_audio_file = getattr(sub_maker, '_actual_audio_file', None) or audio_file
    if actual_audio_file != audio_file:
        logger.info(f"Audio file saved as: {actual_audio_file} (instead of {audio_file})")
        audio_file = actual_audio_file

    # The subtitle provider reports the final word boundary, not the encoded
    # file duration (which also contains codec padding/trailing audio). Planning
    # visuals from that value can be short even after rounding. MoviePy is also
    # what the final combiner uses, so measure the actual file with the same
    # reader and keep the precise float throughout the pipeline.
    try:
        from moviepy import AudioFileClip

        audio_probe = AudioFileClip(audio_file)
        audio_duration = float(audio_probe.duration)
        audio_probe.close()
    except Exception as exc:
        if one_shot.is_enabled(params):
            raise one_shot.OneShotError(
                f"could not measure generated audio before media planning: {exc}"
            ) from exc
        audio_duration = float(math.ceil(voice.get_audio_duration(sub_maker)))
    return audio_file, audio_duration, sub_maker


def generate_subtitle(task_id, params, video_script, sub_maker, audio_file):
    if not params.subtitle_enabled:
        return ""

    subtitle_path = path.join(utils.task_dir(task_id), "subtitle.srt")
    subtitle_provider = config.app.get("subtitle_provider", "edge").strip().lower()
    logger.info(f"\n\n## generating subtitle, provider: {subtitle_provider}")

    # Check if Chatterbox TTS was used by examining the voice name
    is_chatterbox = voice.is_chatterbox_voice(params.voice_name)
    
    subtitle_fallback = False
    if subtitle_provider == "edge":
        if is_chatterbox and sub_maker and sub_maker.subs:
            # Use specialized Chatterbox subtitle function for word-level timestamps
            logger.info("Using Chatterbox-optimized subtitle generation")
            voice.create_chatterbox_subtitle(
                sub_maker=sub_maker, text=video_script, subtitle_file=subtitle_path
            )
        else:
            # Use standard subtitle function for Azure TTS
            voice.create_subtitle(
                text=video_script, sub_maker=sub_maker, subtitle_file=subtitle_path
            )
        
        if not os.path.exists(subtitle_path):
            subtitle_fallback = True
            logger.warning("subtitle file not found, fallback to whisper")

    if subtitle_provider == "whisper" or subtitle_fallback:
        subtitle.create(audio_file=audio_file, subtitle_file=subtitle_path)
        logger.info("\n\n## correcting subtitle")
        subtitle.correct(subtitle_file=subtitle_path, video_script=video_script)

    # Generate enhanced subtitles if word highlighting is enabled
    if getattr(params, 'enable_word_highlighting', False):
        logger.info("\n\n## generating enhanced subtitles for word highlighting")
        enhanced_subtitle_path = path.join(utils.task_dir(task_id), "subtitle_enhanced.json")
        enhanced_subtitles = subtitle.create_enhanced_subtitles(
            audio_file=audio_file, 
            subtitle_file=enhanced_subtitle_path,
            params=params
        )
        if enhanced_subtitles:
            # Store both paths for later use
            params._enhanced_subtitle_path = enhanced_subtitle_path
            logger.info(f"enhanced subtitles created: {enhanced_subtitle_path}")

    subtitle_lines = subtitle.file_to_subtitles(subtitle_path)
    if not subtitle_lines:
        logger.warning(f"subtitle file is invalid: {subtitle_path}")
        return ""

    return subtitle_path


def get_video_materials(task_id, params, video_terms, audio_duration):
    if params.video_source == "local":
        logger.info("\n\n## preprocess local materials")
        materials = video.preprocess_video(
            materials=params.video_materials, clip_duration=params.video_clip_duration
        )
        if not materials:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error(
                "no valid materials found, please check the materials and try again."
            )
            return None
        return [material_info.url for material_info in materials]

    elif params.video_source == "image_search":
        video_script = getattr(params, 'video_script', '') or getattr(params, 'video_subject', '')

        # In one-shot mode the complete hook plan must be supplied up front.
        # Never spend another LLM call trying alternate search wording.
        if one_shot.is_enabled(params):
            hook_term = (
                getattr(params, "hook_cover_term", "")
                or params.video_subject
                or video_script[:160]
            )
        else:
            hook_term = ""
            try:
                hook_term = llm.generate_hook_term(params.video_subject, video_script)
            except Exception as e:
                logger.warning(f"hook term generation failed: {e}")
                hook_term = params.video_subject or ""

        youtube_only_media = bool(getattr(params, "youtube_only_media", False))
        logger.info("\n\n## acquiring visual media")
        _claim_once(params, "material_acquisition")
        if youtube_only_media:
            # This factual sports profile needs the real event, not stock photos,
            # article screenshots or generic football filler.
            image_paths = []
            logger.info("actual-footage-only mode: skipping stock/photo search")
        else:
            image_paths = material.download_images(
                task_id=task_id,
                search_terms=video_terms,
                source=params.video_source,
                audio_duration=audio_duration * params.video_count,
                clip_duration=params.video_clip_duration,
                video_clip_ratio=getattr(params, 'video_clip_ratio', 0.35),
                video_aspect=getattr(params.video_aspect, "value", params.video_aspect) if params.video_aspect else "portrait",
                hook_term=hook_term,
            )
        if not image_paths:
            image_paths = []   # tolerate: real footage below may still carry the video

        # Auto real-footage: download + cut YouTube highlight clips and add them to
        # the pool. They flow through the same CLIP gates / timed-sync as photos,
        # so only on-subject motion footage survives. Best-effort — never fatal.
        if getattr(params, 'enable_youtube_footage', False):
            try:
                from app.services import auto_footage
                from app.models.schema import VideoAspect as _VA
                _vw, _vh = _VA(params.video_aspect).to_resolution()
                raw_terms = video_terms or []
                if isinstance(raw_terms, str):
                    raw_terms = raw_terms.split(",")
                yt_queries = getattr(params, 'youtube_footage_queries', None) or [
                    str(t).strip() for t in raw_terms if str(t).strip()
                ]
                clip_paths = auto_footage.fetch_clips(
                    task_id=task_id,
                    queries=yt_queries,
                    video_width=_vw, video_height=_vh,
                    max_videos=getattr(params, 'youtube_max_videos', 3),
                    clip_len=getattr(params, 'youtube_clip_len', 3.0),
                    clips_per_video=getattr(params, 'youtube_clips_per_video', 5),
                    max_clips=getattr(params, 'youtube_max_clips', 24),
                    max_height=getattr(params, 'youtube_max_height', 720),
                    retries=0 if one_shot.is_enabled(params) else 3,
                )
                if clip_paths:
                    # Front-load real footage so it's preferred by the assigner.
                    image_paths = clip_paths + image_paths
                    logger.success(f"auto_footage: added {len(clip_paths)} real highlight clips to the pool")
            except Exception as e:
                if one_shot.is_enabled(params):
                    raise one_shot.OneShotError(
                        f"real-footage acquisition failed; fallback blocked: {e}"
                    ) from e
                logger.warning(f"auto_footage failed, continuing with image_search only: {e}")

        # Pinned local story photos (additive; no-op if unset). Copied into the
        # task dir, prepended to the pool, exempt from the subject gate, and forced
        # to the opening segments. First = hook/cover.
        _pins = []
        _hook_img = getattr(params, 'hook_image_path', '') or ''
        _intro = list(getattr(params, 'intro_image_paths', None) or [])
        for _src in ([_hook_img] if _hook_img else []) + _intro:
            if _src and os.path.exists(_src):
                try:
                    from PIL import Image as _PILImage
                    _dst = os.path.join(utils.task_dir(task_id), f"pin_{len(_pins)}.jpg")
                    _PILImage.open(_src).convert("RGB").save(_dst, "JPEG", quality=95)
                    _pins.append(_dst)
                except Exception as _e:
                    if one_shot.is_enabled(params):
                        raise one_shot.OneShotError(f"pinned image conversion failed: {_src}: {_e}") from _e
                    logger.warning(f"pin image failed {_src}: {_e}")
        params._pinned_imgs = _pins
        if _pins:
            image_paths = _pins + (image_paths or [])
            logger.success(f"pinned {len(_pins)} local story photos to the pool")

        if not image_paths:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error("failed to download images, no results found for the given search terms.")
            return None

        from app.services import image_ranker

        # Inspect videos too: search results often contain article/lineup graphics
        # encoded as MP4, and those are just as damaging as screenshot images.
        try:
            image_paths = image_ranker.filter_graphics(
                image_paths,
                min_keep=int(getattr(params, "one_shot_min_media", 3) or 3),
                strict=one_shot.is_enabled(params),
            )
        except Exception as e:
            if one_shot.is_enabled(params):
                raise
            logger.warning(f"photo-quality filter failed, keeping all media: {e}")

        # Relevance gate — drop media unrelated to the video subject (CLIP)
        subject_text = params.video_subject or video_script[:200]
        try:
            image_paths = image_ranker.filter_by_relevance(
                image_paths,
                subject_text,
                min_score=getattr(params, 'image_ranking_min_score', 0.18),
                model_name=getattr(params, 'image_similarity_model', 'clip-vit-base-patch32'),
                strict=one_shot.is_enabled(params),
            )
        except Exception as e:
            if one_shot.is_enabled(params):
                raise
            logger.warning(f"relevance filter failed, keeping all media: {e}")

        # Subject-presence gate — drop media that doesn't actually contain the
        # target people/subjects (e.g. random players, stadiums, logos), which
        # the relevance filter alone lets through and which tanks retention.
        if getattr(params, 'enable_subject_gate', False) and getattr(params, 'subject_positive_labels', None):
            logger.info("\n\n## subject-presence gate (verifying target characters are in frame)")
            try:
                image_paths = image_ranker.filter_by_subject_presence(
                    image_paths,
                    positive_labels=params.subject_positive_labels,
                    negative_labels=getattr(params, 'subject_negative_labels', None),
                    margin=getattr(params, 'subject_gate_margin', 0.05),
                    abs_floor=getattr(params, 'subject_gate_abs_floor', 0.0),
                    video_margin=getattr(params, 'subject_gate_video_margin', -0.05),
                    video_abs_floor=getattr(params, 'subject_gate_video_abs_floor', 0.05),
                    model_name=getattr(params, 'image_similarity_model', 'clip-vit-base-patch32'),
                    strict=one_shot.is_enabled(params),
                )
            except Exception as e:
                if one_shot.is_enabled(params):
                    raise
                logger.warning(f"subject-presence gate failed, keeping all media: {e}")

        # Re-add pinned story photos the gate may have dropped (they contain
        # legit non-target subjects like a baby); keep them at the front.
        if getattr(params, '_pinned_imgs', None):
            for _p in reversed(params._pinned_imgs):
                if _p not in image_paths:
                    image_paths.insert(0, _p)

        if one_shot.is_enabled(params):
            min_media = int(getattr(params, "one_shot_min_media", 3) or 3)
            if len(image_paths) < min_media:
                raise one_shot.OneShotError(
                    f"visual gates kept only {len(image_paths)} candidates; "
                    f"{min_media} are required before the only render"
                )

        # Task 3 — pick the COVER/opening image. The first frame decides swipe-away,
        # so prefer a thumb-stopper (the star's FACE / an action shot) via
        # `hook_cover_term`, falling back to the hook-moment term. Matching the
        # literal hook text can land on a boring object (e.g. a document) and spike
        # swipe-away — hence the explicit cover term.
        hook_path = None
        # Pinned hook image wins outright (skip CLIP hook lottery).
        if getattr(params, 'hook_image_path', '') and getattr(params, '_pinned_imgs', None):
            hook_path = params._pinned_imgs[0]
            logger.success(f"hook pinned to local story photo: {os.path.basename(hook_path)}")
        cover_term = getattr(params, 'hook_cover_term', '') or hook_term
        if cover_term and not hook_path:
            try:
                # The hook frame is the #1 thumb-stopper. With auto-footage on,
                # the real clips are reliably the actual player (DDG photos return
                # fans/look-alikes in the same kit that CLIP can't disambiguate),
                # so pick the SHARPEST on-term frame from the clips for the hook.
                if getattr(params, 'enable_youtube_footage', False):
                    _hook_jpg = os.path.join(utils.task_dir(task_id), "hook_cover.jpg")
                    sharp_hook, _hk_src, _hk_t = image_ranker.pick_sharp_subject_frame(
                        image_paths, cover_term, _hook_jpg,
                        min_similarity=getattr(params, 'hook_min_similarity', 0.0),
                        negative_labels=getattr(params, 'hook_negative_labels', None),
                        negative_margin=getattr(params, 'hook_negative_margin', 0.0),
                        model_name=getattr(params, 'image_similarity_model', 'clip-vit-base-patch32'),
                    )
                    if sharp_hook:
                        hook_path = sharp_hook
                        # Remember the SOURCE clip + timestamp so the hook card can
                        # play the real moving footage (not just a still frame).
                        params._hook_clip_path = _hk_src
                        params._hook_clip_start = _hk_t
                if not hook_path and not getattr(params, 'hook_require_video', False):
                    hook_path, _ = image_ranker.pick_best_media(
                        image_paths, cover_term,
                        model_name=getattr(params, 'image_similarity_model', 'clip-vit-base-patch32'),
                    )
                if (one_shot.is_enabled(params)
                        and getattr(params, 'hook_require_video', False)
                        and not getattr(params, '_hook_clip_path', None)):
                    raise one_shot.OneShotError(
                        "no actual video frame cleared the hook similarity/quality gate"
                    )
                logger.info(f"cover/hook frame selected via term: '{cover_term[:60]}'")
            except Exception as e:
                if one_shot.is_enabled(params):
                    raise one_shot.OneShotError(f"hook media selection failed: {e}") from e
                logger.warning(f"hook media selection failed: {e}")

        # Task 1 — CLIP image-to-script ranking
        if getattr(params, 'enable_image_ranking', True):
            logger.info("\n\n## ranking images against script (CLIP)")
            try:
                image_paths = image_ranker.rank_images_for_script(
                    image_paths,
                    video_script,
                    model_name=getattr(params, 'image_similarity_model', 'clip-vit-base-patch32'),
                    min_score=getattr(params, 'image_ranking_min_score', 0.18),
                )
            except Exception as e:
                if one_shot.is_enabled(params):
                    raise one_shot.OneShotError(f"image ranking failed: {e}") from e
                logger.warning(f"image ranking failed, using original order: {e}")

        # Open the short on the hook moment itself
        if hook_path and hook_path in image_paths:
            image_paths.remove(hook_path)
            image_paths.insert(0, hook_path)
        if not hook_path and image_paths:
            hook_path = image_paths[0]

        # Hook card needs a still image — extract a frame if the best match is a clip
        if hook_path and hook_path.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi")):
            frame = image_ranker.extract_video_frame(hook_path, hook_path + ".hook.jpg")
            params._best_image_path = frame or next(
                (p for p in image_paths if not p.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi"))),
                None,
            )
        else:
            params._best_image_path = hook_path

        # Force sequential so ranked/synced order is preserved (Task 1)
        params.video_concat_mode = VideoConcatMode.sequential

        # ── Timed sync — align each image to the caption phrase being spoken ──
        # Each image is shown for exactly its caption's time window, so the right
        # visual lands at the right moment instead of on a fixed clip-duration grid.
        clip_durations = None
        if getattr(params, 'enable_timed_sync', False):
            import json as _json
            enh_path = os.path.join(utils.task_dir(task_id), "subtitle_enhanced.json")
            segments = []
            try:
                with open(enh_path, "r", encoding="utf-8") as f:
                    segments = _json.load(f)
            except Exception as e:
                if one_shot.is_enabled(params):
                    raise one_shot.OneShotError(f"timed sync unavailable: {e}") from e
                logger.warning(f"timed sync: cannot load enhanced subtitles ({e}), skipping sync")
            if segments:
                raw_seg_texts = [s.get("text", "") for s in segments]
                seg_texts = image_ranker.contextualize_segment_texts(
                    raw_seg_texts,
                    video_script,
                    evidence_prompts=getattr(params, 'visual_evidence_prompts', None),
                )
                logger.info("timed sync: caption fragments mapped to sentence-level visual evidence")
                idxs = image_ranker.assign_images_to_segments(
                    image_paths, seg_texts,
                    reuse_penalty=getattr(params, 'segment_reuse_penalty', 0.12),
                    source_reuse_penalty=getattr(params, 'segment_source_reuse_penalty', 0.08),
                    max_media_reuse=getattr(params, 'segment_max_media_reuse', 0),
                    max_source_reuse=getattr(params, 'segment_max_source_reuse', 0),
                    video_bonus=(getattr(params, 'footage_video_bonus', 0.06)
                                 if getattr(params, 'enable_youtube_footage', False) else 0.0),
                    min_video_fraction=(getattr(params, 'footage_min_fraction', 0.5)
                                        if getattr(params, 'enable_youtube_footage', False) else 0.0),
                    min_score=getattr(params, 'segment_assignment_min_score', 0.0),
                    strict=one_shot.is_enabled(params),
                    model_name=getattr(params, 'image_similarity_model', 'clip-vit-base-patch32'),
                )
                synced_paths, clip_durations = [], []
                for s, seg in enumerate(segments):
                    start = float(seg.get("start_time", 0.0))
                    end = float(seg.get("end_time", start))
                    if s + 1 < len(segments):   # close gaps to the next phrase
                        end = float(segments[s + 1].get("start_time", end))
                    synced_paths.append(image_paths[idxs[s]])
                    clip_durations.append(max(0.4, end - start))
                total = sum(clip_durations)
                if audio_duration:
                    # Segment encodes quantize boundaries to video frames. Across
                    # many fast cuts that can remove ~0.2-0.3s even when the planned
                    # durations exactly equal narration. Budget the difference plus
                    # a small tail allowance *before* the only render; the final
                    # compositor trims the harmless overshoot to the voice track.
                    encode_guard = 0.35 if one_shot.is_enabled(params) else 0.0
                    clip_durations[-1] += max(0.0, audio_duration - total) + encode_guard
                # Loop design: make the FINAL visual the same as the opening hook
                # frame so the Short loops seamlessly (strong rewatch/retention signal).
                cover = getattr(params, '_best_image_path', None)
                if cover and synced_paths and not str(synced_paths[-1]).lower().endswith(
                    (".mp4", ".mov", ".webm", ".mkv", ".avi")
                ):
                    synced_paths[-1] = cover
                    logger.info("loop design: final frame set to opening hook image")
                image_paths = synced_paths
                # Pin story photos to the FIRST segments in order (synced to the
                # opening lines), so the reveal opens on them regardless of CLIP.
                if getattr(params, '_pinned_imgs', None):
                    for _i, _p in enumerate(params._pinned_imgs):
                        if _i < len(image_paths):
                            image_paths[_i] = _p
                    logger.info(f"pinned {len(params._pinned_imgs)} photos to opening segments")
                params.video_clip_duration = int(max(clip_durations)) + 1   # no truncation
                logger.info(
                    f"timed sync: aligned {len(image_paths)} images to {len(segments)} caption "
                    f"phrases (planned visual {sum(clip_durations):.2f}s vs "
                    f"audio {audio_duration:.2f}s)"
                )

        # Task 2 — Ken Burns 2.0: pass motion style
        from app.models.schema import MaterialInfo as MI, VideoAspect
        vw, vh = VideoAspect(params.video_aspect).to_resolution()
        image_materials = [MI(url=p, provider="image_search") for p in image_paths]
        processed = video.preprocess_video(
            materials=image_materials,
            clip_duration=params.video_clip_duration,
            motion_style=getattr(params, 'image_motion_style', 'varied'),
            durations=clip_durations,
            video_width=vw,
            video_height=vh,
            fill_mode=getattr(params, 'image_fill_mode', 'cover'),
            color_grade=getattr(params, 'enable_color_grade', True),
            cover_min_keep=getattr(params, 'cover_min_keep', 0.62),
        )
        if not processed:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error("failed to convert images to video clips.")
            return None
        return [m.url for m in processed]

    else:
        logger.info(f"\n\n## downloading videos from {params.video_source}")
        downloaded_videos = material.download_videos(
            task_id=task_id,
            search_terms=video_terms,
            source=params.video_source,
            video_aspect=params.video_aspect,
            video_contact_mode=params.video_concat_mode,
            audio_duration=audio_duration * params.video_count,
            max_clip_duration=params.video_clip_duration,
        )
        if not downloaded_videos:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error(
                "failed to download videos, maybe the network is not available. if you are in China, please use a VPN."
            )
            return None
        return downloaded_videos


def generate_final_videos(
    task_id, params, downloaded_videos, audio_file, subtitle_path, video_script=""
):
    final_video_paths = []
    combined_video_paths = []
    
    if one_shot.is_enabled(params) and params.video_count != 1:
        raise one_shot.OneShotError("one-shot mode cannot render multiple variants")

    # Force random mode for multiple videos to ensure variety
    # Semantic mode would produce identical videos, which doesn't make sense for multiple generation
    video_concat_mode = params.video_concat_mode
    if params.video_count > 1 and video_concat_mode.value == "semantic":
        logger.info(f"🔄 Multiple videos requested ({params.video_count}), forcing random concatenation mode for variety")
        logger.info("   ℹ️  Semantic mode would produce identical videos, which is not useful for multiple generation")
        video_concat_mode = VideoConcatMode.random
    
    video_transition_mode = params.video_transition_mode

    _progress = 50
    for i in range(params.video_count):
        index = i + 1
        combined_video_path = path.join(
            utils.task_dir(task_id), f"combined-{index}.mp4"
        )
        logger.info(f"\n\n## combining video: {index} => {combined_video_path}")
        video.combine_videos(
            combined_video_path=combined_video_path,
            video_paths=downloaded_videos,
            audio_file=audio_file,
            video_aspect=params.video_aspect,
            video_concat_mode=video_concat_mode,
            video_transition_mode=video_transition_mode,
            max_clip_duration=params.video_clip_duration,
            threads=params.n_threads,
            script=video_script,
            params=params,
        )

        _progress += 50 / params.video_count / 2
        sm.state.update_task(task_id, progress=_progress)

        final_video_path = path.join(utils.task_dir(task_id), f"final-{index}.mp4")

        logger.info(f"\n\n## generating video: {index} => {final_video_path}")
        rendered_duration = video.generate_video(
            video_path=combined_video_path,
            audio_path=audio_file,
            subtitle_path=subtitle_path,
            output_file=final_video_path,
            params=params,
        )
        params._rendered_duration = rendered_duration

        _progress += 50 / params.video_count / 2
        sm.state.update_task(task_id, progress=_progress)

        final_video_paths.append(final_video_path)
        combined_video_paths.append(combined_video_path)

    return final_video_paths, combined_video_paths


def _start_impl(task_id, params: VideoParams, stop_at: str = "video"):
    logger.info(f"start task: {task_id}, stop_at: {stop_at}")
    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=5)

    if type(params.video_concat_mode) is str:
        params.video_concat_mode = VideoConcatMode(params.video_concat_mode)

    # 0. Comparison / match-cut PHONK series — a self-contained, voiceover-free
    #    path. Inert unless comparison_mode is True, so the normal pipeline below
    #    is completely unaffected when the flag is off (default).
    if getattr(params, "comparison_mode", False):
        logger.info("comparison_mode ON — building match-cut phonk short (no voiceover)")
        try:
            _claim_once(params, "comparison_render")
            result = video.build_comparison_short(task_id, params)
        except Exception as e:
            logger.error(f"comparison_mode build failed: {e}")
            result = None
        if result and result.get("videos"):
            sm.state.update_task(task_id, state=const.TASK_STATE_COMPLETE, progress=100, **result)
        else:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return result

    # 1. Generate script
    video_script = generate_script(task_id, params)
    if not video_script or "Error: " in video_script:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=10)

    if stop_at == "script":
        sm.state.update_task(
            task_id, state=const.TASK_STATE_COMPLETE, progress=100, script=video_script
        )
        return {"script": video_script}

    # 2. Generate terms
    video_terms = ""
    if params.video_source != "local":
        video_terms = generate_terms(task_id, params, video_script)
        if not video_terms:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            return

    save_script_data(task_id, video_script, video_terms, params)

    if stop_at == "terms":
        sm.state.update_task(
            task_id, state=const.TASK_STATE_COMPLETE, progress=100, terms=video_terms
        )
        return {"script": video_script, "terms": video_terms}

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=20)

    # 3. Generate audio
    audio_file, audio_duration, sub_maker = generate_audio(
        task_id, params, video_script
    )
    if not audio_file:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return
    # Speech-aware visual target: the encoded file duration includes codec
    # padding/trailing silence after the last spoken word, which the visual
    # track doesn't need to cover. video.py's combiner reads this back via
    # `_required_visual_duration` to avoid padding the edit for dead air.
    try:
        last_word_end = voice.get_audio_duration(sub_maker)
        if last_word_end > 0 and last_word_end <= audio_duration:
            params._required_visual_duration = last_word_end
    except Exception as exc:
        logger.debug(f"could not compute speech-aware visual duration: {exc}")
    if one_shot.is_enabled(params):
        max_audio_seconds = float(
            getattr(params, "one_shot_max_audio_seconds", 0.0) or 0.0
        )
        if max_audio_seconds > 0 and float(audio_duration) > max_audio_seconds:
            raise one_shot.OneShotError(
                f"sole narration is {float(audio_duration):.2f}s, above the "
                f"{max_audio_seconds:.2f}s retention ceiling; acquisition/render blocked"
            )

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=30)

    if stop_at == "audio":
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            audio_file=audio_file,
        )
        return {"audio_file": audio_file, "audio_duration": audio_duration}

    # 4. Generate subtitle
    subtitle_path = generate_subtitle(
        task_id, params, video_script, sub_maker, audio_file
    )
    if one_shot.is_enabled(params) and params.subtitle_enabled and not subtitle_path:
        raise one_shot.OneShotError("subtitle generation failed; captionless render blocked")

    if stop_at == "subtitle":
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            subtitle_path=subtitle_path,
        )
        return {"subtitle_path": subtitle_path}

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=40)

    # 5. Get video materials
    downloaded_videos = get_video_materials(
        task_id, params, video_terms, audio_duration
    )
    if not downloaded_videos:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    if stop_at == "materials":
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_COMPLETE,
            progress=100,
            materials=downloaded_videos,
        )
        return {"materials": downloaded_videos}

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=50)

    # Task 3 — Generate hook text and store best image on params
    if getattr(params, 'enable_hook_card', True) and params.video_source == "image_search":
        hook_text = getattr(params, 'hook_text', '').strip()
        if not hook_text:
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError("hook_text missing after one-shot preflight")
            try:
                hook_text = llm.generate_hook(params.video_subject, video_script)
            except Exception as e:
                logger.warning(f"hook text generation failed: {e}")
                hook_text = " ".join(params.video_subject.upper().split()[:5])
        params._hook_text = hook_text
        hook_image = getattr(params, '_best_image_path', None)
        if not hook_image and downloaded_videos:
            from app.services import image_ranker
            hook_image = image_ranker.extract_video_frame(
                downloaded_videos[0], downloaded_videos[0] + ".hook.jpg"
            ) or None
        params._hook_image_path = hook_image
        logger.info(f"hook text: '{hook_text}'")

    # Structural media validation happens before the only final render. It may
    # reject a bad plan, but it never searches/renders again automatically.
    if one_shot.is_enabled(params):
        params._media_quality_report = one_shot.validate_media_plan(
            downloaded_videos,
            audio_duration,
            min_media=int(getattr(params, "one_shot_min_media", 3) or 3),
            min_sources=int(getattr(params, "one_shot_min_visual_sources", 0) or 0),
            image_duration=float(getattr(params, "video_clip_duration", 2) or 2),
        )

    # 6. Generate final videos
    _claim_once(params, "final_render")
    final_video_paths, combined_video_paths = generate_final_videos(
        task_id, params, downloaded_videos, audio_file, subtitle_path, video_script
    )

    if not final_video_paths:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        return

    quality_report = None
    if one_shot.is_enabled(params):
        expected_duration = getattr(params, "_rendered_duration", None) or audio_duration
        quality_report = one_shot.validate_render(final_video_paths[0], expected_duration)
        quality_report["media_plan"] = getattr(params, "_media_quality_report", {})
        report_path = path.join(utils.task_dir(task_id), "quality_report.json")
        with open(report_path, "w", encoding="utf-8") as handle:
            handle.write(utils.to_json(quality_report))

    logger.success(
        f"task {task_id} finished, generated {len(final_video_paths)} videos."
    )

    kwargs = {
        "videos": final_video_paths,
        "combined_videos": combined_video_paths,
        "script": video_script,
        "terms": video_terms,
        "audio_file": audio_file,
        "audio_duration": audio_duration,
        "subtitle_path": subtitle_path,
        "materials": downloaded_videos,
        "quality_report": quality_report,
    }
    sm.state.update_task(
        task_id, state=const.TASK_STATE_COMPLETE, progress=100, **kwargs
    )
    return kwargs


def start(task_id, params: VideoParams, stop_at: str = "video"):
    """Run once, fail closed, and never convert an internal failure into a retry."""
    if not one_shot.is_enabled(params):
        return _start_impl(task_id, params, stop_at)

    guard = None
    try:
        one_shot.apply_growth_profile(params)
        report = one_shot.preflight(params, stop_at=stop_at)
        with one_shot.generation_slot(task_id=task_id):
            guard = one_shot.OneShotGuard(task_id, params, report)
            params._one_shot_guard = guard

            params.video_count = 1

            result = _start_impl(task_id, params, stop_at)
            if result and (stop_at != "video" or result.get("videos")):
                guard.finish(
                    "complete",
                    output=(result.get("videos") or [None])[0] if isinstance(result, dict) else None,
                    quality_report=result.get("quality_report") if isinstance(result, dict) else None,
                )
            else:
                guard.finish("failed", error="pipeline returned no valid output; retry blocked")
            return result
    except Exception as exc:
        logger.exception(f"one-shot task {task_id} failed; no retry will be attempted: {exc}")
        if guard:
            guard.finish("failed", error=str(exc))
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_FAILED,
            error=str(exc),
            one_shot=True,
        )
        return {"error": str(exc), "one_shot": True, "retry_attempted": False}


if __name__ == "__main__":
    task_id = "task_id"
    params = VideoParams(
        video_subject="金钱的作用",
        voice_name="zh-CN-XiaoyiNeural-Female",
        voice_rate=1.0,
    )
    start(task_id, params, stop_at="video")

#!/usr/bin/env python3

import glob
import itertools
import os
import random
import gc
import shutil
import json
import re
from typing import List
from loguru import logger
import numpy as np
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    afx,
    concatenate_videoclips,
)
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import ImageFont, ImageDraw, Image

from app.models import const
from app.models.schema import (
    MaterialInfo,
    VideoAspect,
    VideoConcatMode,
    VideoParams,
    VideoTransitionMode,
)
from app.services.utils import video_effects
from app.utils import utils
from app.services import semantic_video

# High-quality video encoding settings
audio_codec = "aac"
video_codec = "libx264"
fps = 30

# High-quality encoding parameters
video_bitrate = "8000k"  # High bitrate for excellent quality
audio_bitrate = "320k"   # High audio bitrate
crf = 18                 # Constant Rate Factor - lower = higher quality (18-23 is excellent range)
preset = "medium"        # Balance between encoding speed and compression efficiency

# FFmpeg parameters for maximum quality
quality_params = [
    "-crf", str(crf),
    "-preset", preset,
    "-profile:v", "high",
    "-level", "4.1",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart"
]

class SubClippedVideoClip:
    def __init__(self, file_path, start_time=None, end_time=None, width=None, height=None, duration=None):
        self.file_path = file_path
        self.start_time = start_time
        self.end_time = end_time
        self.width = width
        self.height = height
        if duration is None:
            self.duration = end_time - start_time
        else:
            self.duration = duration

    def __str__(self):
        return f"SubClippedVideoClip(file_path={self.file_path}, start_time={self.start_time}, end_time={self.end_time}, duration={self.duration}, width={self.width}, height={self.height})"


def close_clip(clip):
    if clip is None:
        return
        
    try:
        # close main resources
        if hasattr(clip, 'reader') and clip.reader is not None:
            clip.reader.close()
            
        # close audio resources
        if hasattr(clip, 'audio') and clip.audio is not None:
            if hasattr(clip.audio, 'reader') and clip.audio.reader is not None:
                clip.audio.reader.close()
            del clip.audio
            
        # close mask resources
        if hasattr(clip, 'mask') and clip.mask is not None:
            if hasattr(clip.mask, 'reader') and clip.mask.reader is not None:
                clip.mask.reader.close()
            del clip.mask
            
        # handle child clips in composite clips
        if hasattr(clip, 'clips') and clip.clips:
            for child_clip in clip.clips:
                if child_clip is not clip:  # avoid possible circular references
                    close_clip(child_clip)
            
        # clear clip list
        if hasattr(clip, 'clips'):
            clip.clips = []
            
    except Exception as e:
        logger.error(f"failed to close clip: {str(e)}")
    
    del clip
    gc.collect()

def delete_files(files: List[str] | str):
    if isinstance(files, str):
        files = [files]
        
    for file in files:
        try:
            os.remove(file)
        except OSError:
            pass

def get_bgm_file(bgm_type: str = "random", bgm_file: str = ""):
    if not bgm_type:
        return ""

    if bgm_file and os.path.exists(bgm_file):
        return bgm_file

    if bgm_type == "random":
        suffix = "*.mp3"
        song_dir = utils.song_dir()
        files = glob.glob(os.path.join(song_dir, suffix))
        return random.choice(files)

    return ""


def combine_videos(
    combined_video_path: str,
    video_paths: List[str],
    audio_file: str,
    video_aspect: VideoAspect = VideoAspect.portrait,
    video_concat_mode: VideoConcatMode = VideoConcatMode.random,
    video_transition_mode: VideoTransitionMode = None,
    max_clip_duration: int = 5,
    threads: int = 2,
    script: str = "",
    params: VideoParams = None
) -> str:
    audio_clip = AudioFileClip(audio_file)
    audio_duration = audio_clip.duration
    required_visual_duration = float(
        getattr(params, "_required_visual_duration", audio_duration) or audio_duration
    ) if params else float(audio_duration)
    logger.info(f"audio duration: {audio_duration} seconds")
    if required_visual_duration < audio_duration:
        logger.info(
            f"speech-aware visual target: {required_visual_duration:.2f}s "
            f"({audio_duration - required_visual_duration:.2f}s trailing audio silence excluded)"
        )
    # Required duration of each clip
    req_dur = audio_duration / len(video_paths)
    req_dur = max_clip_duration
    logger.info(f"maximum clip duration: {req_dur} seconds")
    output_dir = os.path.dirname(combined_video_path)

    aspect = VideoAspect(video_aspect)
    video_width, video_height = aspect.to_resolution()

    # Check if semantic mode is enabled
    if video_concat_mode.value == "semantic" and script:
        logger.info("Using semantic video selection mode")
        
        # Load video metadata
        video_metadata = []
        for video_path in video_paths:
            metadata = semantic_video.load_video_metadata(video_path)
            if metadata:
                video_metadata.append(metadata)
            else:
                logger.debug(f"No metadata found for {video_path}, using filename")
                filename = os.path.splitext(os.path.basename(video_path))[0]
                metadata = {
                    'video_path': video_path,
                    'search_term': filename,
                    'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0,
                    'created_at': os.path.getctime(video_path) if os.path.exists(video_path) else 0
                }
                video_metadata.append(metadata)
        
        # Use semantic video selection
        selected_videos = semantic_video.select_videos_for_script(
            script=script,
            video_metadata=video_metadata,
            audio_duration=audio_duration,
            max_clip_duration=max_clip_duration,
            similarity_threshold=params.similarity_threshold if params else 0.5,
            diversity_threshold=params.diversity_threshold if params else 5,
            max_video_reuse=params.max_video_reuse if params else 2,
            min_segment_length=params.min_segment_length if params else 25,
            semantic_model=params.semantic_model if params else "all-mpnet-base-v2",
            enable_image_similarity=params.enable_image_similarity if params else False,
            image_similarity_threshold=params.image_similarity_threshold if params else 0.7,
            image_similarity_model=params.image_similarity_model if params else "clip-vit-base-patch32"
        )
        
        # Process selected videos
        processed_clips = []
        video_duration = 0
        max_reuse_limit = params.max_video_reuse if params and hasattr(params, 'max_video_reuse') and params.max_video_reuse is not None else None
        
        for i, selection in enumerate(selected_videos):
            # Don't break early when max_video_reuse=1 to utilize all selected videos
            if video_duration > audio_duration and not (max_reuse_limit and max_reuse_limit == 1):
                break
                
            video_path = selection['video_path']
            target_duration = min(selection['duration'], max_clip_duration)
            
            logger.debug(f"processing semantic clip {i+1}: {os.path.basename(video_path)}, target duration: {target_duration:.2f}s")
            
            try:
                clip = VideoFileClip(video_path)
                clip_duration = min(clip.duration, target_duration)
                
                # Random start time for variety
                max_start = max(0, clip.duration - clip_duration)
                start_time = random.uniform(0, max_start) if max_start > 0 else 0
                
                clip = clip.subclipped(start_time, start_time + clip_duration)
                
                # Resize clip if needed
                clip_w, clip_h = clip.size
                if clip_w != video_width or clip_h != video_height:
                    clip_ratio = clip.w / clip.h
                    video_ratio = video_width / video_height
                    logger.debug(f"resizing clip, source: {clip_w}x{clip_h}, ratio: {clip_ratio:.2f}, target: {video_width}x{video_height}, ratio: {video_ratio:.2f}")
                    
                    if clip_ratio == video_ratio:
                        clip = clip.resized(new_size=(video_width, video_height))
                    else:
                        # COVER: scale to FILL the frame then center-crop the
                        # overflow, so the image fills all of 9:16 with no black bars.
                        if clip_ratio > video_ratio:
                            # source wider than target → match height, crop sides
                            scale_factor = video_height / clip_h
                        else:
                            # source taller than target → match width, crop top/bottom
                            scale_factor = video_width / clip_w

                        new_width = int(clip_w * scale_factor)
                        new_height = int(clip_h * scale_factor)

                        clip_resized = clip.resized(new_size=(new_width, new_height)).with_position("center")
                        # Composite sized to the target frame crops the overflow.
                        clip = CompositeVideoClip([clip_resized], size=(video_width, video_height))
                
                # Apply transitions if specified
                if video_transition_mode and video_transition_mode.value != VideoTransitionMode.none.value:
                    shuffle_side = random.choice(["left", "right", "top", "bottom"])
                    if video_transition_mode.value == VideoTransitionMode.fade_in.value:
                        clip = video_effects.fadein_transition(clip, 1)
                    elif video_transition_mode.value == VideoTransitionMode.fade_out.value:
                        clip = video_effects.fadeout_transition(clip, 1)
                    elif video_transition_mode.value == VideoTransitionMode.slide_in.value:
                        clip = video_effects.slidein_transition(clip, 1, shuffle_side)
                    elif video_transition_mode.value == VideoTransitionMode.slide_out.value:
                        clip = video_effects.slideout_transition(clip, 1, shuffle_side)
                    elif video_transition_mode.value == VideoTransitionMode.shuffle.value:
                        transition_funcs = [
                            lambda c: video_effects.fadein_transition(c, 1),
                            lambda c: video_effects.fadeout_transition(c, 1),
                            lambda c: video_effects.slidein_transition(c, 1, shuffle_side),
                            lambda c: video_effects.slideout_transition(c, 1, shuffle_side),
                        ]
                        shuffle_transition = random.choice(transition_funcs)
                        clip = shuffle_transition(clip)
                
                # Write clip to temp file
                clip_file = f"{output_dir}/temp-semantic-clip-{i+1}.mp4"
                clip.write_videofile(
                    clip_file, 
                    logger=None, 
                    fps=fps, 
                    codec=video_codec,
                    bitrate=video_bitrate,
                    audio_bitrate=audio_bitrate,
                    ffmpeg_params=quality_params
                )
                
                close_clip(clip)
                
                processed_clips.append(SubClippedVideoClip(file_path=clip_file, duration=clip_duration, width=clip_w, height=clip_h))
                video_duration += clip_duration
                
            except Exception as e:
                logger.error(f"failed to process semantic clip: {str(e)}")
                if params:
                    from app.services import one_shot
                    if one_shot.is_enabled(params):
                        raise one_shot.OneShotError(
                            f"semantic clip processing failed; fallback blocked: {e}"
                        ) from e
        
    else:
        # Original random/sequential logic
        processed_clips = []
        subclipped_items = []
        video_duration = 0
        for video_path in video_paths:
            clip = VideoFileClip(video_path)
            clip_duration = clip.duration
            clip_w, clip_h = clip.size
            close_clip(clip)
            
            start_time = 0

            while start_time < clip_duration:
                end_time = min(start_time + max_clip_duration, clip_duration)
                # Keep this chunk if it's a full max-length chunk OR the first chunk
                # of the clip (so clips shorter than max_clip_duration aren't dropped —
                # required for timed-sync phrase clips, which are often < max).
                if clip_duration - start_time >= max_clip_duration or start_time == 0:
                    subclipped_items.append(SubClippedVideoClip(file_path= video_path, start_time=start_time, end_time=end_time, width=clip_w, height=clip_h))
                start_time = end_time
                if video_concat_mode.value == VideoConcatMode.sequential.value:
                    break

        # random subclipped_items order
        if video_concat_mode.value == VideoConcatMode.random.value:
            random.shuffle(subclipped_items)
            
        logger.debug(f"total subclipped items: {len(subclipped_items)}")
        
        # Add downloaded clips over and over until the duration of the audio (max_duration) has been reached
        for i, subclipped_item in enumerate(subclipped_items):
            if video_duration > audio_duration:
                break
            
            logger.debug(f"processing clip {i+1}: {subclipped_item.width}x{subclipped_item.height}, current duration: {video_duration:.2f}s, remaining: {audio_duration - video_duration:.2f}s")
            
            try:
                clip = VideoFileClip(subclipped_item.file_path).subclipped(subclipped_item.start_time, subclipped_item.end_time)
                clip_duration = clip.duration
                # Not all videos are same size, so we need to resize them
                clip_w, clip_h = clip.size
                if clip_w != video_width or clip_h != video_height:
                    clip_ratio = clip.w / clip.h
                    video_ratio = video_width / video_height
                    logger.debug(f"resizing clip, source: {clip_w}x{clip_h}, ratio: {clip_ratio:.2f}, target: {video_width}x{video_height}, ratio: {video_ratio:.2f}")
                    
                    if clip_ratio == video_ratio:
                        clip = clip.resized(new_size=(video_width, video_height))
                    else:
                        # COVER: scale to FILL the frame then center-crop the
                        # overflow, so the image fills all of 9:16 with no black bars.
                        if clip_ratio > video_ratio:
                            # source wider than target → match height, crop sides
                            scale_factor = video_height / clip_h
                        else:
                            # source taller than target → match width, crop top/bottom
                            scale_factor = video_width / clip_w

                        new_width = int(clip_w * scale_factor)
                        new_height = int(clip_h * scale_factor)

                        clip_resized = clip.resized(new_size=(new_width, new_height)).with_position("center")
                        # Composite sized to the target frame crops the overflow.
                        clip = CompositeVideoClip([clip_resized], size=(video_width, video_height))
                        
                shuffle_side = random.choice(["left", "right", "top", "bottom"])
                if video_transition_mode and video_transition_mode.value == VideoTransitionMode.none.value:
                    clip = clip
                elif video_transition_mode and video_transition_mode.value == VideoTransitionMode.fade_in.value:
                    clip = video_effects.fadein_transition(clip, 1)
                elif video_transition_mode and video_transition_mode.value == VideoTransitionMode.fade_out.value:
                    clip = video_effects.fadeout_transition(clip, 1)
                elif video_transition_mode and video_transition_mode.value == VideoTransitionMode.slide_in.value:
                    clip = video_effects.slidein_transition(clip, 1, shuffle_side)
                elif video_transition_mode and video_transition_mode.value == VideoTransitionMode.slide_out.value:
                    clip = video_effects.slideout_transition(clip, 1, shuffle_side)
                elif video_transition_mode and video_transition_mode.value == VideoTransitionMode.shuffle.value:
                    transition_funcs = [
                        lambda c: video_effects.fadein_transition(c, 1),
                        lambda c: video_effects.fadeout_transition(c, 1),
                        lambda c: video_effects.slidein_transition(c, 1, shuffle_side),
                        lambda c: video_effects.slideout_transition(c, 1, shuffle_side),
                    ]
                    shuffle_transition = random.choice(transition_funcs)
                    clip = shuffle_transition(clip)

                if clip.duration > max_clip_duration:
                    clip = clip.subclipped(0, max_clip_duration)
                    
                # wirte clip to temp file
                clip_file = f"{output_dir}/temp-clip-{i+1}.mp4"
                clip.write_videofile(
                    clip_file, 
                    logger=None, 
                    fps=fps, 
                    codec=video_codec,
                    bitrate=video_bitrate,
                    audio_bitrate=audio_bitrate,
                    ffmpeg_params=quality_params
                )
                
                close_clip(clip)
            
                processed_clips.append(SubClippedVideoClip(file_path=clip_file, duration=clip.duration, width=clip_w, height=clip_h))
                video_duration += clip.duration
                
            except Exception as e:
                logger.error(f"failed to process clip: {str(e)}")
                if params:
                    from app.services import one_shot
                    if one_shot.is_enabled(params):
                        raise one_shot.OneShotError(
                            f"clip processing failed; fallback blocked: {e}"
                        ) from e
    
    # Codec/frame quantization can make a carefully timed fast-cut plan a few
    # frames shorter than the audio container. In strict mode allow only the
    # same 200ms structural tolerance used by the pre-render media gate; the
    # final compositor trims both streams to their safe shared duration.
    strict_one_shot = False
    if params:
        from app.services import one_shot
        strict_one_shot = one_shot.is_enabled(params)
    coverage_tolerance = 0.2 if strict_one_shot else 0.0

    # loop processed clips until the video duration matches or exceeds the audio duration.
    if video_duration + coverage_tolerance < required_visual_duration:
        if params:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(
                    f"render plan is short ({video_duration:.2f}s visual vs "
                    f"{required_visual_duration:.2f}s required speech coverage); "
                    "automatic clip looping blocked"
                )
        # Check if we should respect max_video_reuse setting (already defined for semantic mode)
        if 'max_reuse_limit' not in locals():
            max_reuse_limit = params.max_video_reuse if params and hasattr(params, 'max_video_reuse') and params.max_video_reuse is not None else None
        
        if max_reuse_limit and max_reuse_limit == 1:
            # User has set max reuse to 1, don't loop clips
            logger.warning(f"video duration ({video_duration:.2f}s) is shorter than audio duration ({audio_duration:.2f}s), but max_video_reuse is set to 1 - NOT looping clips.")
            logger.info(f"final video duration: {video_duration:.2f}s, audio duration: {audio_duration:.2f}s")
        else:
            # Original looping behavior for other cases
            logger.warning(f"video duration ({video_duration:.2f}s) is shorter than audio duration ({audio_duration:.2f}s), looping clips to match audio length.")
            
            if max_reuse_limit:
                # Track how many times each clip has been used for reuse limit
                clip_usage = {}
                base_clips = processed_clips.copy()
                original_clip_count = len(base_clips)
                
                # Initialize usage counter
                for i, clip in enumerate(base_clips):
                    clip_usage[i] = 1  # Already used once
                
                clip_cycle = itertools.cycle(enumerate(base_clips))
                clips_added = 0
                
                for clip_idx, clip in clip_cycle:
                    if video_duration >= audio_duration:
                        break
                    
                    # Check if this clip has reached the reuse limit
                    if clip_usage[clip_idx] >= max_reuse_limit:
                        # Skip clips that have reached the reuse limit
                        continue
                    
                    processed_clips.append(clip)
                    video_duration += clip.duration
                    clip_usage[clip_idx] += 1
                    clips_added += 1
                    
                    # Safety check: if all clips have reached the limit, break
                    if all(usage >= max_reuse_limit for usage in clip_usage.values()):
                        logger.warning(f"all clips have reached max reuse limit ({max_reuse_limit}), stopping at {video_duration:.2f}s")
                        break
                
                logger.info(f"video duration: {video_duration:.2f}s, audio duration: {audio_duration:.2f}s, looped {clips_added} clips (respecting max_reuse_limit: {max_reuse_limit})")
            else:
                # Original unlimited looping behavior
                base_clips = processed_clips.copy()
                for clip in itertools.cycle(base_clips):
                    if video_duration >= audio_duration:
                        break
                    processed_clips.append(clip)
                    video_duration += clip.duration
                logger.info(f"video duration: {video_duration:.2f}s, audio duration: {audio_duration:.2f}s, looped {len(processed_clips)-len(base_clips)} clips")
    elif video_duration < required_visual_duration:
        logger.info(
            f"accepting {required_visual_duration - video_duration:.2f}s frame-quantization "
            "shortfall within one-shot tolerance"
        )
     
    # merge video clips using direct concatenation to avoid quality degradation
    logger.info("starting clip merging process")
    if not processed_clips:
        logger.warning("no clips available for merging")
        return combined_video_path
    
    # Write cut times for SFX (Task 5)
    _write_cut_times(output_dir, [c.duration for c in processed_clips])

    # if there is only one clip, use it directly
    if len(processed_clips) == 1:
        logger.info("using single clip directly")
        shutil.copy(processed_clips[0].file_path, combined_video_path)
        delete_files([processed_clips[0].file_path])
        logger.info("video combining completed")
        return combined_video_path
    
    # Load all clips at once and concatenate in single operation to preserve quality
    logger.info(f"loading {len(processed_clips)} clips for direct concatenation")
    clips_to_merge = []
    
    try:
        for i, clip_info in enumerate(processed_clips):
            logger.info(f"loading clip {i+1}/{len(processed_clips)}: {os.path.basename(clip_info.file_path)}")
            clip = VideoFileClip(clip_info.file_path)
            clips_to_merge.append(clip)
        
        # Concatenate all clips in single operation - NO QUALITY LOSS!
        logger.info("concatenating all clips in single operation")
        final_clip = concatenate_videoclips(clips_to_merge)
        
        # Write final result with high quality settings
        logger.info("writing final concatenated video with high quality")
        final_clip.write_videofile(
            combined_video_path,
            threads=threads,
            logger=None,
            temp_audiofile_path=output_dir,
            audio_codec=audio_codec,
            fps=fps,
            codec=video_codec,
            bitrate=video_bitrate,
            audio_bitrate=audio_bitrate,
            ffmpeg_params=quality_params
        )
        
        # Clean up clips
        for clip in clips_to_merge:
            close_clip(clip)
        close_clip(final_clip)
        
    except Exception as e:
        logger.error(f"failed to concatenate clips: {str(e)}")
        if params:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(
                    f"direct concatenation failed; progressive re-render blocked: {e}"
                ) from e
        # Fallback to progressive merging if direct concatenation fails
        logger.warning("falling back to progressive merging")
        return _progressive_merge_fallback(processed_clips, combined_video_path, output_dir, threads)
    
    # clean temp files
    clip_files = [clip.file_path for clip in processed_clips]
    delete_files(clip_files)
            
    logger.info("video combining completed")
    return combined_video_path


def _write_cut_times(output_dir: str, clip_durations: list):
    """Write cumulative cut times to cut_times.json for SFX (Task 5)."""
    try:
        cut_times = []
        t = 0.0
        for d in clip_durations[:-1]:  # skip last — no cut after final clip
            t += d
            cut_times.append(round(t, 3))
        with open(os.path.join(output_dir, "cut_times.json"), "w") as f:
            json.dump(cut_times, f)
    except Exception as e:
        logger.debug(f"cut_times write failed: {e}")


def _progressive_merge_fallback(processed_clips, combined_video_path, output_dir, threads):
    """Fallback progressive merging method if direct concatenation fails"""
    logger.info("using progressive merge fallback")
    
    # create initial video file as base
    base_clip_path = processed_clips[0].file_path
    temp_merged_video = f"{output_dir}/temp-merged-video.mp4"
    temp_merged_next = f"{output_dir}/temp-merged-next.mp4"
    
    # copy first clip as initial merged video
    shutil.copy(base_clip_path, temp_merged_video)
    
    # merge remaining video clips one by one
    for i, clip in enumerate(processed_clips[1:], 1):
        logger.info(f"merging clip {i}/{len(processed_clips)-1}, duration: {clip.duration:.2f}s")
        
        try:
            # load current base video and next clip to merge
            base_clip = VideoFileClip(temp_merged_video)
            next_clip = VideoFileClip(clip.file_path)
            
            # merge these two clips
            merged_clip = concatenate_videoclips([base_clip, next_clip])

            # save merged result to temp file
            merged_clip.write_videofile(
                filename=temp_merged_next,
                threads=threads,
                logger=None,
                temp_audiofile_path=output_dir,
                audio_codec=audio_codec,
                fps=fps,
                codec=video_codec,
                bitrate=video_bitrate,
                audio_bitrate=audio_bitrate,
                ffmpeg_params=quality_params
            )
            close_clip(base_clip)
            close_clip(next_clip)
            close_clip(merged_clip)
            
            # replace base file with new merged file
            delete_files(temp_merged_video)
            os.rename(temp_merged_next, temp_merged_video)
            
        except Exception as e:
            logger.error(f"failed to merge clip: {str(e)}")
            continue
    
    # after merging, rename final result to target file name
    os.rename(temp_merged_video, combined_video_path)
    
    # clean temp files
    clip_files = [clip.file_path for clip in processed_clips]
    delete_files(clip_files)
    
    return combined_video_path


def wrap_text(text, max_width, font="Arial", fontsize=60):
    # Create ImageFont
    font = ImageFont.truetype(font, fontsize)

    def get_text_size(inner_text):
        inner_text = inner_text.strip()
        left, top, right, bottom = font.getbbox(inner_text)
        return right - left, bottom - top

    width, height = get_text_size(text)
    if width <= max_width:
        return text, height

    processed = True
    _wrapped_lines_ = []
    words = text.split(" ")
    _txt_ = ""
    
    # Improved word wrapping with better line balancing
    for word in words:
        _before = _txt_
        test_txt = _txt_ + f"{word} " if _txt_ else f"{word} "
        _width, _height = get_text_size(test_txt)
        
        if _width <= max_width:
            _txt_ = test_txt
        else:
            if _txt_.strip() == word.strip():
                # Single word is too long, force break
                processed = False
                break
            
            # Add current line and start new line
            _wrapped_lines_.append(_before.strip())
            _txt_ = f"{word} "
    
    # Add remaining text
    if _txt_.strip():
        _wrapped_lines_.append(_txt_.strip())
    
    if processed:
        # Balance line lengths for better visual appearance
        _wrapped_lines_ = _balance_line_lengths(_wrapped_lines_, font, max_width)
        result = "\n".join(_wrapped_lines_)
        height = len(_wrapped_lines_) * height
        return result, height

    # Fallback: character-by-character wrapping
    _wrapped_lines_ = []
    chars = list(text)
    _txt_ = ""
    for char in chars:
        test_txt = _txt_ + char
        _width, _height = get_text_size(test_txt)
        if _width <= max_width:
            _txt_ = test_txt
        else:
            if _txt_:
                _wrapped_lines_.append(_txt_)
            _txt_ = char
    
    if _txt_:
        _wrapped_lines_.append(_txt_)
    
    result = "\n".join(_wrapped_lines_)
    height = len(_wrapped_lines_) * height
    return result, height


def _balance_line_lengths(lines, font, max_width):
    """
    Balance line lengths for better visual appearance when center-aligned
    """
    if len(lines) <= 1:
        return lines
    
    def get_text_width(text):
        left, top, right, bottom = font.getbbox(text.strip())
        return right - left
    
    balanced_lines = []
    
    for i, line in enumerate(lines):
        if i < len(lines) - 1:  # Not the last line
            current_line_width = get_text_width(line)
            next_line = lines[i + 1]
            
            # Try to balance by moving words between lines
            words_current = line.split()
            words_next = next_line.split()
            
            # If current line is much shorter than max width and next line has words
            if current_line_width < max_width * 0.7 and len(words_next) > 1:
                # Try moving first word from next line to current line
                test_line = line + " " + words_next[0]
                test_width = get_text_width(test_line)
                
                if test_width <= max_width:
                    # Move the word
                    balanced_lines.append(test_line)
                    lines[i + 1] = " ".join(words_next[1:])  # Update next line
                    continue
        
        balanced_lines.append(line)
    
    return balanced_lines


# Power words → emoji sticker that pops in when the word is spoken. First match wins.
_EMOJI_MAP = [
    (("goat", "greatest", "legend", "legendary", "best"), "🐐"),
    (("worldcup", "world", "cup", "trophy", "trophies", "ballon", "champion", "champions", "title"), "🏆"),
    (("died", "death", "dead", "die", "dies"), "💀"),
    (("broke", "broken", "neck", "injury", "injured", "crash"), "🤕"),
    (("cry", "crying", "cried", "tears", "tear"), "😭"),
    (("napkin",), "🧾"),
    (("money", "dollars", "dollar", "million", "millions", "rich", "fortune", "paid"), "💰"),
    (("never", "impossible", "unbelievable", "shocked", "stunned", "insane", "crazy"), "🤯"),
    (("goal", "goals", "scored", "score", "scores"), "⚽"),
    (("unstoppable", "fire", "magic", "genius"), "🔥"),
    (("god", "miracle", "prayed"), "🙏"),
    (("heart", "love"), "❤️"),
]
# Shock words flash RED instead of gold — adds the hand-picked emphasis a human editor does.
_SHOCK_WORDS = {
    "never", "died", "death", "dead", "broke", "broken", "cry", "crying", "tears",
    "shocked", "stunned", "impossible", "unbelievable", "worst", "destroyed",
    "humiliation", "nightmare", "tragedy", "betrayed", "alone",
}


def _word_emoji(word: str):
    w = "".join(c for c in word.lower() if c.isalpha())
    if not w:
        return None
    for keys, emoji in _EMOJI_MAP:
        if w in keys:
            return emoji
    return None


def _render_emoji_img(ch: str, px: int):
    """Render a color emoji to an RGBA PIL image ~px tall. Apple Color Emoji only
    supports the 160 strike, so render at 160 then downscale. Returns None on failure."""
    try:
        from PIL import ImageFont as _IF
        f = _IF.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)
        canvas = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        ImageDraw.Draw(canvas).text((10, 10), ch, font=f, embedded_color=True)
        bbox = canvas.getbbox()
        if not bbox:
            return None
        canvas = canvas.crop(bbox)
        w, h = canvas.size
        nw = max(2, int(w * px / h))
        return canvas.resize((nw, px), Image.LANCZOS)
    except Exception as e:
        logger.warning(f"emoji render failed for {ch!r}: {e}")
        return None


def create_enhanced_subtitle_clips(enhanced_subtitle_path, params, video_width, video_height, font_path):
    """
    Create text clips with true word-by-word highlighting
    Creates subtitle images where only the currently spoken word is highlighted
    """
    text_clips = []
    
    # Load enhanced subtitle data
    with open(enhanced_subtitle_path, 'r', encoding='utf-8') as f:
        enhanced_data = json.load(f)
    
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def position_clip(clip, params, video_height):
        """Apply positioning to a clip based on subtitle position settings"""
        if params.subtitle_position == "bottom":
            return clip.with_position(("center", video_height * 0.85))
        elif params.subtitle_position == "top":
            return clip.with_position(("center", video_height * 0.05))
        elif params.subtitle_position == "custom":
            custom_y = (video_height * params.custom_position / 100)
            return clip.with_position(("center", custom_y))
        else:  # center
            return clip.with_position(("center", "center"))
    
    def create_word_highlighted_image(text, highlighted_word_indices, font_size, normal_color, highlight_color, stroke_color, stroke_width):
        """Create an image with specific words highlighted"""
        try:
            font = ImageFont.truetype(font_path, font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()
        
        # Clean text: remove commas but keep line breaks they indicate
        # Replace comma + space with just space, and standalone commas with nothing
        cleaned_text = text.replace(', ', ' ').replace(',', ' ')
        
        # Wrap text using the same logic
        max_width = int(video_width * 0.9)
        wrapped_txt, _ = wrap_text(
            cleaned_text, max_width=max_width, font=font_path, fontsize=font_size
        )
        
        # Split into lines and words
        lines = wrapped_txt.split('\n')
        
        # Bigger font for the active word — Hormozi-style size emphasis
        try:
            big_font = ImageFont.truetype(font_path, int(font_size * 1.26))
        except (IOError, OSError):
            big_font = font

        # Calculate image dimensions (tall enough for the enlarged word)
        line_height = int(font_size * 1.26 * 1.32)
        img_height = len(lines) * line_height + 40  # Add padding
        img_width = max_width + 80  # Add padding (room for the bigger word)
        
        # Create transparent image
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Colors
        normal_rgb = hex_to_rgb(normal_color)
        highlight_rgb = hex_to_rgb(highlight_color)
        stroke_rgb = hex_to_rgb(stroke_color) if stroke_color else None
        
        word_index = 0
        y_pos = 20
        
        for line in lines:
            words = line.split()
            
            # Calculate total line width (per-word font: active word is bigger)
            line_width = 0
            for k, word in enumerate(words):
                wf = big_font if (word_index + k) in highlighted_word_indices else font
                word_bbox = wf.getbbox(word + ' ')
                line_width += word_bbox[2] - word_bbox[0]
            
            # Center the line
            x_pos = (img_width - line_width) // 2
            x_pos = max(20, x_pos)  # Ensure minimum padding
            
            for word in words:
                is_hl = word_index in highlighted_word_indices
                wf = big_font if is_hl else font
                word_color = highlight_rgb if is_hl else normal_rgb
                # Vertical-center this word within the line (handles mixed sizes)
                wb = wf.getbbox(word)
                wh = wb[3] - wb[1]
                y_word = y_pos + (line_height - wh) // 2 - wb[1]
                # Draw word with stroke if specified (thicker stroke on the big word)
                if stroke_rgb and stroke_width > 0:
                    stroke_w = int(stroke_width) + (1 if is_hl else 0)
                    for dx in range(-stroke_w, stroke_w + 1):
                        for dy in range(-stroke_w, stroke_w + 1):
                            if dx != 0 or dy != 0:
                                draw.text((x_pos + dx, y_word + dy), word, font=wf, fill=stroke_rgb)
                # Draw main text
                draw.text((x_pos, y_word), word, font=wf, fill=word_color)
                # Calculate next position
                word_bbox = wf.getbbox(word + ' ')
                x_pos += word_bbox[2] - word_bbox[0]
                word_index += 1
            
            y_pos += line_height
        
        return img
    
    def create_subtitle_clip(text, highlighted_word_indices, start_time, duration, params, animate=False, hl_color=None):
        """Create a subtitle clip with specified highlighting"""
        try:
            img = create_word_highlighted_image(
                text=text,
                highlighted_word_indices=highlighted_word_indices,
                font_size=int(params.font_size),
                normal_color=params.text_fore_color,
                highlight_color=hl_color or params.word_highlight_color,
                stroke_color=params.stroke_color,
                stroke_width=int(params.stroke_width)
            )

            clip = ImageClip(np.array(img)).with_duration(duration).with_start(start_time)
            if animate and duration > 0:
                # CapCut/Hormozi-style pop: overshoot to 1.14 and settle to 1.0
                # over ~0.13s as each word becomes active. Reads as animated captions.
                clip = clip.resized(lambda t: 1.0 + 0.14 * (1 - min(t / 0.13, 1.0)))
            return position_clip(clip, params, video_height)

        except Exception as e:
            logger.error(f"Failed to create subtitle clip: {str(e)}")
            return None
    
    last_emoji_end = -10.0  # spacing so emoji stickers don't clutter
    for subtitle_data in enhanced_data:
        start_time = subtitle_data['start_time']
        end_time = subtitle_data['end_time']
        text = subtitle_data['text']
        words = subtitle_data['words']
        
        # Sort words by start time
        sorted_words = sorted(words, key=lambda w: w['start'])
        
        # Create word mapping to indices
        text_words = []
        for line in text.split('\n'):
            text_words.extend(line.split())
        
        # Create time segments with word highlighting
        current_time = start_time
        
        for word_data in sorted_words:
            word_start = max(word_data['start'], start_time)
            word_end = min(word_data['end'], end_time)
            word_text = word_data['word'].strip()
            
            if word_start >= word_end:
                continue
            
            # Find word index in text
            word_index = -1
            for idx, text_word in enumerate(text_words):
                if text_word.strip().lower() == word_text.lower():
                    word_index = idx
                    break
            
            # Create segment before word (normal colors)
            if word_start > current_time:
                clip = create_subtitle_clip(text, set(), current_time, word_start - current_time, params)
                if clip:
                    text_clips.append(clip)
            
            # Create highlighted segment during word (pop animation; shock words flash red)
            if word_index >= 0:
                is_shock = "".join(c for c in word_text.lower() if c.isalpha()) in _SHOCK_WORDS
                hl = "#FF2D2D" if is_shock else None
                clip = create_subtitle_clip(text, {word_index}, word_start, word_end - word_start, params, animate=True, hl_color=hl)
                if clip:
                    text_clips.append(clip)

            # Emoji sticker pop on power words (spaced ≥1.2s apart so it doesn't clutter)
            emoji = _word_emoji(word_text)
            if emoji and word_start - last_emoji_end >= 1.2:
                em_img = _render_emoji_img(emoji, int(video_height * 0.11))
                if em_img is not None:
                    em_dur = min(1.4, max(0.8, end_time - word_start))
                    em_clip = ImageClip(np.array(em_img)).with_start(word_start).with_duration(em_dur)

                    def _epop(t):
                        if t < 0.13:
                            return max(0.08, 1.3 * (t / 0.13))      # scale 0 → 1.3 (pop)
                        if t < 0.26:
                            return 1.3 - 0.3 * ((t - 0.13) / 0.13)  # 1.3 → 1.0 (settle)
                        return 1.0

                    em_clip = em_clip.resized(_epop).with_position(("center", int(video_height * 0.30)))
                    text_clips.append(em_clip)
                    last_emoji_end = word_start

            current_time = word_end
        
        # Create final normal segment if needed
        if current_time < end_time:
            clip = create_subtitle_clip(text, set(), current_time, end_time - current_time, params)
            if clip:
                text_clips.append(clip)
    
    return text_clips


def _split_emoji(text: str):
    """Return (text_without_emoji, first_emoji_char_or_None). Regular fonts render
    emoji as tofu boxes, so we strip them and composite a real color emoji instead."""
    emoji = None
    kept = []
    for ch in text:
        cp = ord(ch)
        is_emoji = (
            0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF
            or cp in (0x2705, 0x274C, 0x2B50, 0x2728) or 0xFE00 <= cp <= 0xFE0F
        )
        if is_emoji:
            if emoji is None and not (0xFE00 <= cp <= 0xFE0F):
                emoji = ch
        else:
            kept.append(ch)
    return "".join(kept).strip(), emoji


def _render_text_card(
    text: str, font_path: str, font_size: int,
    video_width: int, video_height: int,
    text_color=(255, 255, 255), stroke_color=(0, 0, 0), stroke_width: int = 8,
    y_center_ratio: float = 0.45, bg_alpha: int = 0,
) -> Image.Image:
    """Render a centred text image (RGBA) using PIL for hook/CTA cards.
    Any emoji in `text` is rendered as a real color glyph centred below the text."""
    text, _emoji_char = _split_emoji(text)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    # Word-wrap
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= video_width * 0.88:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)

    lh = int(font_size * 1.25)
    total_h = lh * len(lines) + 20
    img = Image.new("RGBA", (video_width, video_height), (0, 0, 0, bg_alpha))
    draw = ImageDraw.Draw(img)
    y_start = int(video_height * y_center_ratio) - total_h // 2

    for line in lines:
        bbox = font.getbbox(line)
        lw = bbox[2] - bbox[0]
        x = (video_width - lw) // 2
        # Stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y_start + dy), line, font=font, fill=(*stroke_color, 255))
        draw.text((x, y_start), line, font=font, fill=(*text_color, 255))
        y_start += lh

    # Composite a real color emoji centred just below the text (regular fonts can't
    # render it — without this it shows as a tofu box).
    if _emoji_char:
        em = _render_emoji_img(_emoji_char, int(font_size * 1.05))
        if em is not None:
            ex = (video_width - em.width) // 2
            ey = y_start + int(font_size * 0.15)
            img.alpha_composite(em, (ex, ey))

    return img


def create_hook_clip(
    image_path: str, hook_text: str, params, video_width: int, video_height: int
):
    """
    Task 3 — first `hook_duration` seconds: cover image + dark veil + big hook text.
    Returns a VideoClip overlay (no audio, starts at t=0).
    """
    hook_dur = float(getattr(params, 'hook_duration', 1.5))
    font_path = os.path.join(utils.font_dir(), getattr(params, 'font_name', 'STHeitiMedium.ttc'))
    font_size = int(video_width * 0.082)
    font_size = font_size if font_size % 2 == 0 else font_size + 1

    # --- MOVING-VIDEO hook: play the real footage clip the cover came from, with
    #     a dark veil + hook text on top. Far more thumb-stopping than a still. ---
    clip_path = getattr(params, '_hook_clip_path', None)
    clip_start = float(getattr(params, '_hook_clip_start', 0.0) or 0.0)
    if clip_path and os.path.exists(clip_path):
        try:
            src = VideoFileClip(clip_path)
            sdur = float(src.duration or hook_dur)
            seg = min(hook_dur, sdur)
            st = max(0.0, min(clip_start - seg / 2.0, max(0.0, sdur - seg)))
            vclip = src.subclipped(st, st + seg)
            # cover-crop to fill 9:16
            cw, ch = vclip.size
            cr, fr = cw / ch, video_width / video_height
            sf = (video_height / ch) if cr > fr else (video_width / cw)
            vclip = vclip.resized(new_size=(max(2, int(cw * sf)), max(2, int(ch * sf)))).with_position("center")
            # punch-in zoom for energy — but NOT in seamless-loop mode. The loop-back
            # already settles the title in at the END, so re-punching the footage at the
            # START makes the intro re-animate right after the seam (reads as a gap). In
            # loop mode the footage continues at a steady 1.0 scale (it ends the loop-back
            # at 1.0 too) so the restart is a direct, continuous continuation, not a new
            # appearance animation.
            if not getattr(params, 'loop_seamless', False):
                vclip = vclip.resized(lambda t: 1.0 + 0.12 * (1 - (1 - min(t / max(seg, 0.1), 1)) ** 2))
            # dark veil + baked hook text as a transparent overlay
            hook_opacity = max(0.0, min(0.8, float(getattr(params, 'hook_overlay_opacity', 0.45))))
            veil_text = Image.new("RGBA", (video_width, video_height), (0, 0, 0, int(255 * hook_opacity)))
            text_layer = _render_text_card(
                hook_text, font_path, font_size, video_width, video_height,
                y_center_ratio=0.42, bg_alpha=0,
            )
            veil_text = Image.alpha_composite(veil_text, text_layer)
            overlay = ImageClip(np.array(veil_text)).with_duration(seg)
            return CompositeVideoClip(
                [vclip, overlay.with_position("center")], size=(video_width, video_height)
            ).with_start(0)
        except Exception as e:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(
                    f"moving hook footage failed; static fallback blocked: {e}"
                ) from e
            logger.warning(f"hook card: moving-video hook failed ({e}), falling back to still")

    # --- Background image (cover-crop to fill frame) ---
    try:
        bg = Image.open(image_path).convert("RGB")
        bg_ratio = bg.width / bg.height
        frame_ratio = video_width / video_height
        if bg_ratio > frame_ratio:
            new_h = video_height
            new_w = int(new_h * bg_ratio)
        else:
            new_w = video_width
            new_h = int(new_w / bg_ratio)
        new_w = new_w if new_w % 2 == 0 else new_w + 1
        new_h = new_h if new_h % 2 == 0 else new_h + 1
        bg = bg.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - video_width) // 2
        top = (new_h - video_height) // 2
        bg = bg.crop((left, top, left + video_width, top + video_height))
    except Exception as e:
        from app.services import one_shot
        if one_shot.is_enabled(params):
            raise one_shot.OneShotError(f"hook image failed to load: {e}") from e
        logger.warning(f"hook card: failed to load image {image_path}: {e}")
        bg = Image.new("RGB", (video_width, video_height), (10, 10, 10))

    # --- Dark overlay (45% opacity) ---
    hook_opacity = max(0.0, min(0.8, float(getattr(params, 'hook_overlay_opacity', 0.45))))
    overlay = Image.new("RGBA", (video_width, video_height), (0, 0, 0, int(255 * hook_opacity)))
    bg_rgba = bg.convert("RGBA")
    bg_with_veil = Image.alpha_composite(bg_rgba, overlay).convert("RGB")

    # --- Hook text baked in ---
    text_layer = _render_text_card(
        hook_text, font_path, font_size, video_width, video_height,
        y_center_ratio=0.42, bg_alpha=0,
    )
    bg_rgba2 = bg_with_veil.convert("RGBA")
    composite = Image.alpha_composite(bg_rgba2, text_layer).convert("RGB")

    hook_img_clip = ImageClip(np.array(composite)).with_duration(hook_dur)

    # Fast zoom 1.0 → 1.20 on the hook card — skipped in seamless-loop mode so the
    # start is a direct, static continuation of the settled loop-back (no re-animation).
    d = hook_dur
    if getattr(params, 'loop_seamless', False):
        return CompositeVideoClip([hook_img_clip.with_position("center")], size=(video_width, video_height)).with_start(0)
    zoomed = hook_img_clip.resized(lambda t: 1.0 + 0.20 * (1 - (1 - min(t / d, 1)) ** 2))
    return CompositeVideoClip([zoomed.with_position("center")], size=(video_width, video_height)).with_start(0)


def create_follow_tag(params, video_width: int, video_height: int, video_duration: float):
    """Loop-safe persistent follow nudge: a small semi-transparent tag near the
    bottom, present for the WHOLE video — identical at the loop seam, so it never
    signals 'the end'. Returns an overlay clip or None."""
    try:
        font_path = os.path.join(utils.font_dir(), getattr(params, 'font_name', 'STHeitiMedium.ttc'))
        fsize = int(video_width * 0.040)
        fsize = fsize if fsize % 2 == 0 else fsize + 1
        layer = _render_text_card(
            "FOLLOW +", font_path, fsize, video_width, video_height,
            stroke_width=4, y_center_ratio=0.93, bg_alpha=0,
        )
        return (
            ImageClip(np.array(layer))
            .with_duration(video_duration)
            .with_start(0)
            .with_opacity(0.78)
        )
    except Exception as e:
        logger.warning(f"follow tag failed: {e}")
        return None


def create_midroll_cta(params, video_width: int, video_height: int, video_duration: float):
    """A brief CTA after the payoff, not at frame zero and not at the loop seam.

    It preserves the invisible ending while still giving high-intent viewers a
    reason to subscribe. The old persistent FOLLOW tag asked before delivering
    value and was visible for the entire Short.
    """
    from moviepy import vfx

    duration = min(0.9, max(0.6, video_duration * 0.07))
    start = min(max(0.0, video_duration * 0.68), max(0.0, video_duration - duration - 2.0))
    font_path = os.path.join(utils.font_dir(), getattr(params, "font_name", "STHeitiMedium.ttc"))
    font_size = int(video_width * 0.046)
    font_size += font_size % 2
    layer = _render_text_card(
        getattr(params, "cta_text", "FOLLOW FOR MORE"),
        font_path,
        font_size,
        video_width,
        video_height,
        stroke_width=5,
        y_center_ratio=0.84,
        bg_alpha=0,
    )
    fade = min(0.14, duration / 3)
    return (
        ImageClip(np.array(layer))
        .with_duration(duration)
        .with_start(start)
        .with_opacity(0.92)
        .with_effects([vfx.CrossFadeIn(fade), vfx.CrossFadeOut(fade)])
    )


def create_loopback_clip(params, video_width: int, video_height: int, video_duration: float):
    """Seamless visual loop-back. Instead of replaying the hook moment with a reset
    zoom (which read as a ~1s freeze/stall at the loop seam), this LEADS the footage
    UP TO the opening hook frame so the last frame ≈ the first frame: same footage
    moment, the zoom LANDS on 1.0 (matching the opening hook's start scale → no snap),
    and the hook veil+title fade back in over the tail so the title doesn't pop on at
    the restart. Net effect: the Short restarts invisibly. Falls back to a clean still
    of the hook image if no clip is available; None if neither exists."""
    from moviepy import vfx
    seg = min(1.4, max(0.7, video_duration * 0.10))
    clip_path = getattr(params, '_hook_clip_path', None)
    clip_start = float(getattr(params, '_hook_clip_start', 0.0) or 0.0)
    hook_dur = float(getattr(params, 'hook_duration', 1.5))
    hook_text = getattr(params, '_hook_text', '') or ''
    if clip_path and os.path.exists(clip_path):
        try:
            src = VideoFileClip(clip_path)
            sdur = float(src.duration or seg)
            s = min(seg, sdur)
            # The opening hook plays footage starting here; END the loop-back on this
            # exact frame so its last frame == the opening's first frame (continuous
            # motion across the seam, no jump).
            st_hook = max(0.0, min(clip_start - hook_dur / 2.0, max(0.0, sdur - hook_dur)))
            st = max(0.0, st_hook - s)
            vclip = src.subclipped(st, st + s)
            cw, ch = vclip.size
            cr, fr = cw / ch, video_width / video_height
            sf = (video_height / ch) if cr > fr else (video_width / cw)
            vclip = vclip.resized(new_size=(max(2, int(cw * sf)), max(2, int(ch * sf))))
            # Gentle push that LANDS on 1.0 to match the opening hook's starting scale.
            vclip = vclip.resized(lambda t: 1.05 - 0.05 * min(t / max(s, 0.1), 1.0))
            layers = [vclip.with_position("center")]
            # Fade the hook veil + title back in over the tail so the final frame looks
            # like the opening hook card → the restart is invisible (no text pop).
            if hook_text:
                try:
                    font_path = os.path.join(utils.font_dir(), getattr(params, 'font_name', 'STHeitiMedium.ttc'))
                    fsize = int(video_width * 0.082)
                    fsize = fsize if fsize % 2 == 0 else fsize + 1
                    hook_opacity = max(0.0, min(0.8, float(getattr(params, 'hook_overlay_opacity', 0.45))))
                    veil_text = Image.new("RGBA", (video_width, video_height), (0, 0, 0, int(255 * hook_opacity)))
                    text_layer = _render_text_card(
                        hook_text, font_path, fsize, video_width, video_height,
                        y_center_ratio=0.42, bg_alpha=0,
                    )
                    veil_text = Image.alpha_composite(veil_text, text_layer)
                    fade = min(max(0.4, s * 0.5), s)
                    ov = (
                        ImageClip(np.array(veil_text))
                        .with_duration(fade)
                        .with_start(max(0.0, s - fade))
                        .with_position("center")
                        .with_effects([vfx.CrossFadeIn(min(fade, max(0.25, fade * 0.8)))])
                    )
                    layers.append(ov)
                except Exception as e:
                    logger.warning(f"loopback veil/title overlay failed: {e}")
            comp = CompositeVideoClip(layers, size=(video_width, video_height)).with_duration(s)
            # Dissolve the loop-back in from the body footage (no hard cut into it).
            comp = comp.with_effects([vfx.CrossFadeIn(min(0.4, s * 0.4))])
            return comp.with_start(max(0.0, video_duration - s))
        except Exception as e:
            logger.warning(f"loopback clip failed, falling back to still: {e}")
    return create_cta_clip(params, video_width, video_height, video_duration, loop_mode=True)


def create_cta_clip(params, video_width: int, video_height: int, video_duration: float, loop_mode: bool = False):
    """
    Task 6 — last 2 seconds: dark overlay + CTA text.
    Returns a VideoClip overlay starting at video_duration - 2.
    In loop_mode: no dark veil and no end-text — just re-show the opening hook
    image cleanly so the last frame matches frame 1 (seamless visual loop-back).
    """
    cta_dur = 2.0
    cta_start = max(0.0, video_duration - cta_dur)
    cta_text = '' if loop_mode else getattr(params, 'cta_text', 'FOLLOW FOR MORE')
    font_path = os.path.join(utils.font_dir(), getattr(params, 'font_name', 'STHeitiMedium.ttc'))
    font_size = int(video_width * 0.075)
    font_size = font_size if font_size % 2 == 0 else font_size + 1

    # Loop design: end on the SAME hook face (darkened) + CTA text, so the Short
    # loops seamlessly back into the opening hook card (top retention signal).
    cover_path = getattr(params, '_hook_image_path', None) or getattr(params, '_best_image_path', None)
    bg = None
    if cover_path and os.path.exists(cover_path):
        try:
            im = Image.open(cover_path).convert("RGB")
            r, fr = im.width / im.height, video_width / video_height
            if r > fr:
                nh = video_height; nw = int(nh * r)
            else:
                nw = video_width; nh = int(nw / r)
            nw += nw % 2; nh += nh % 2
            im = im.resize((nw, nh), Image.LANCZOS)
            l = (nw - video_width) // 2
            t = max(0, min(int((nh - video_height) * 0.30), nh - video_height))
            im = im.crop((l, t, l + video_width, t + video_height))
            if loop_mode:
                bg = im  # clean loop-back, no veil
            else:
                veil = Image.new("RGBA", (video_width, video_height), (0, 0, 0, int(255 * 0.60)))
                bg = Image.alpha_composite(im.convert("RGBA"), veil).convert("RGB")
        except Exception as e:
            logger.warning(f"cta cover bg failed: {e}")

    # Loop mode with no cover image: skip the overlay entirely so the last footage
    # clip plays out (circular audio carries the loop).
    if loop_mode and bg is None:
        return None

    if bg is not None:
        text_layer = _render_text_card(
            cta_text, font_path, font_size, video_width, video_height,
            y_center_ratio=0.50, bg_alpha=0,
        )
        composite = Image.alpha_composite(bg.convert("RGBA"), text_layer).convert("RGB")
        cta_img_clip = ImageClip(np.array(composite)).with_duration(cta_dur).with_start(cta_start)
    else:
        text_img = _render_text_card(
            cta_text, font_path, font_size, video_width, video_height,
            y_center_ratio=0.50, bg_alpha=int(255 * 0.60),
        )
        cta_img_clip = (
            ImageClip(np.array(text_img.convert("RGB")))
            .with_duration(cta_dur)
            .with_start(cta_start)
            .with_opacity(0.92)
        )
    return cta_img_clip


def _speech_end_time(audio_path: str, total_dur: float):
    """Return the timestamp of the LAST spoken word in the voiceover (i.e. where the
    trailing silence begins), or None. Used in seamless-loop mode to trim dead air so
    the circular voiceover's last word flows straight into its first word on restart."""
    try:
        import subprocess as _sp
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ff = "ffmpeg"
        cmd = [ff, "-hide_banner", "-i", audio_path,
               "-af", "silencedetect=n=-40dB:d=0.25", "-f", "null", "-"]
        r = _sp.run(cmd, capture_output=True, text=True, timeout=60)
        starts, ends = [], []
        for line in r.stderr.splitlines():
            if "silence_start:" in line:
                try: starts.append(float(line.split("silence_start:")[1].strip().split()[0]))
                except Exception: pass
            if "silence_end:" in line:
                try: ends.append(float(line.split("silence_end:")[1].split("|")[0].strip()))
                except Exception: pass
        # A trailing silence block whose end ≈ the file end means speech stopped at its
        # start. Only trust it if it leaves a sensible amount of speech in front.
        if starts and ends and abs(ends[-1] - total_dur) < 0.35 and 1.0 < starts[-1] < total_dur:
            return starts[-1]
    except Exception as e:
        logger.warning(f"speech-end detect failed: {e}")
    return None


def generate_video(
    video_path: str,
    audio_path: str,
    subtitle_path: str,
    output_file: str,
    params: VideoParams,
):
    aspect = VideoAspect(params.video_aspect)
    video_width, video_height = aspect.to_resolution()

    logger.info(f"generating video: {video_width} x {video_height}")
    logger.info(f"  ① video: {video_path}")
    logger.info(f"  ② audio: {audio_path}")
    logger.info(f"  ③ subtitle: {subtitle_path}")
    logger.info(f"  ④ output: {output_file}")

    # https://github.com/harry0703/MoneyPrinterTurbo/issues/217
    # PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: 'final-1.mp4.tempTEMP_MPY_wvf_snd.mp3'
    # write into the same directory as the output file
    output_dir = os.path.dirname(output_file)

    font_path = ""
    if params.subtitle_enabled:
        if not params.font_name:
            params.font_name = "STHeitiMedium.ttc"
        font_path = os.path.join(utils.font_dir(), params.font_name)
        if os.name == "nt":
            font_path = font_path.replace("\\", "/")

        logger.info(f"  ⑤ font: {font_path}")

    def create_text_clip(subtitle_item):
        params.font_size = int(params.font_size)
        params.stroke_width = int(params.stroke_width)
        phrase = subtitle_item[1]
        
        # Clean text: remove commas but keep spaces for readability
        cleaned_phrase = phrase.replace(', ', ' ').replace(',', ' ')
        
        max_width = video_width * 0.9
        wrapped_txt, txt_height = wrap_text(
            cleaned_phrase, max_width=max_width, font=font_path, fontsize=params.font_size
        )
        interline = int(params.font_size * 0.25)
        size=(int(max_width), int(txt_height + params.font_size * 0.25 + (interline * (wrapped_txt.count("\n") + 1))))

        _clip = TextClip(
            text=wrapped_txt,
            font=font_path,
            font_size=params.font_size,
            color=params.text_fore_color,
            bg_color=params.text_background_color,
            stroke_color=params.stroke_color,
            stroke_width=params.stroke_width,
            method='caption',  # Use caption method for better text wrapping
            size=size,
            # align='center',  # Removed - not supported in MoviePy 2.2.1
            # interline=interline,
        )
        duration = subtitle_item[0][1] - subtitle_item[0][0]
        _clip = _clip.with_start(subtitle_item[0][0])
        _clip = _clip.with_end(subtitle_item[0][1])
        _clip = _clip.with_duration(duration)
        if params.subtitle_position == "bottom":
            _clip = _clip.with_position(("center", video_height * 0.95 - _clip.h))
        elif params.subtitle_position == "top":
            _clip = _clip.with_position(("center", video_height * 0.05))
        elif params.subtitle_position == "custom":
            # Ensure the subtitle is fully within the screen bounds
            margin = 10  # Additional margin, in pixels
            max_y = video_height - _clip.h - margin
            min_y = margin
            custom_y = (video_height - _clip.h) * (params.custom_position / 100)
            custom_y = max(
                min_y, min(custom_y, max_y)
            )  # Constrain the y value within the valid range
            _clip = _clip.with_position(("center", custom_y))
        else:  # center
            _clip = _clip.with_position(("center", "center"))
        return _clip

    video_clip = VideoFileClip(video_path).without_audio()
    # Global black-and-white on footage only (before colored overlays composite on top)
    if getattr(params, 'enable_grayscale', False):
        from moviepy.video.fx.BlackAndWhite import BlackAndWhite
        video_clip = video_clip.with_effects([BlackAndWhite()])
        logger.info("grayscale applied to footage")
    audio_clip = AudioFileClip(audio_path).with_effects(
        [afx.MultiplyVolume(params.voice_volume)]
    )

    # --- Seamless-loop tight trim: cut the dead air after the last spoken word so the
    #     circular voiceover loops within ~200ms (last word → first word on restart).
    #     The footage is built to >= audio length (overshoot by whole clips) AND the TTS
    #     leaves trailing silence; both are removed here. Loop mode only; additive. ---
    if getattr(params, 'loop_seamless', False) and getattr(params, 'loop_tight_trim', True):
        try:
            sp_end = _speech_end_time(audio_path, audio_clip.duration)
            tail = float(getattr(params, 'loop_tail_pad', 0.12))
            loop_end = (sp_end + tail) if sp_end else min(audio_clip.duration, video_clip.duration)
            loop_end = max(1.5, min(loop_end, video_clip.duration, audio_clip.duration + tail))
            if loop_end + 0.05 < video_clip.duration:
                video_clip = video_clip.subclipped(0, loop_end)
            if loop_end < audio_clip.duration:
                audio_clip = audio_clip.subclipped(0, loop_end)
            logger.info(f"loop tight-trim: speech_end={sp_end}, loop_end={loop_end:.2f}s "
                        f"(was video {video_clip.duration:.2f}s / audio {audio_clip.duration:.2f}s)")
        except Exception as e:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(f"loop tight-trim failed: {e}") from e
            logger.warning(f"loop tight-trim failed: {e}")

    # Clip concatenation intentionally overshoots to guarantee coverage. Remove
    # that silent visual tail for every mode so the payoff/CTA lands against the
    # real narration ending instead of one or two seconds of dead footage.
    exact_end = min(float(video_clip.duration), float(audio_clip.duration))
    if video_clip.duration > exact_end + 0.03:
        video_clip = video_clip.subclipped(0, exact_end)
    if audio_clip.duration > exact_end + 0.03:
        audio_clip = audio_clip.subclipped(0, exact_end)

    def make_textclip(text):
        return TextClip(
            text=text,
            font=font_path,
            font_size=params.font_size,
        )

    # --- Subtitle / word-highlight layer ---
    overlay_clips = []

    if subtitle_path and os.path.exists(subtitle_path):
        enhanced_subtitle_path = getattr(params, '_enhanced_subtitle_path', None)
        use_word_highlighting = (
            getattr(params, 'enable_word_highlighting', True) and
            enhanced_subtitle_path and
            os.path.exists(enhanced_subtitle_path)
        )

        if use_word_highlighting:
            logger.info("Using enhanced subtitles with word highlighting")
            text_clips = create_enhanced_subtitle_clips(
                enhanced_subtitle_path, params, video_width, video_height, font_path
            )
        else:
            sub = SubtitlesClip(
                subtitles=subtitle_path, encoding="utf-8", make_textclip=make_textclip
            )
            text_clips = []
            for item in sub.subtitles:
                clip = create_text_clip(subtitle_item=item)
                text_clips.append(clip)

        overlay_clips.extend(text_clips)

    # --- Task 3: Hook card overlay (first hook_duration seconds) ---
    hook_image_path = getattr(params, '_hook_image_path', None)
    hook_text = getattr(params, '_hook_text', '')
    if getattr(params, 'enable_hook_card', True) and hook_image_path and hook_text:
        try:
            hook_clip = create_hook_clip(hook_image_path, hook_text, params, video_width, video_height)
            overlay_clips.append(hook_clip)
            logger.info(f"hook card added: '{hook_text}'")
        except Exception as e:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(f"hook overlay failed: {e}") from e
            logger.error(f"failed to create hook card: {e}")

    # --- Task 6: CTA overlay / seamless loop-back (last ~2 seconds) ---
    loop_mode = getattr(params, 'loop_seamless', False)
    if loop_mode:
        try:
            loopback = create_loopback_clip(params, video_width, video_height, video_clip.duration)
            if loopback is not None:
                overlay_clips.append(loopback)
            if getattr(params, 'loop_follow_tag', True):
                tag = create_follow_tag(params, video_width, video_height, video_clip.duration)
                if tag is not None:
                    overlay_clips.append(tag)
            if getattr(params, 'enable_cta', True):
                overlay_clips.append(
                    create_midroll_cta(params, video_width, video_height, video_clip.duration)
                )
            logger.info("seamless loop mode: no terminal CTA card, clean visual loop-back")
        except Exception as e:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(f"loop/CTA overlay failed: {e}") from e
            logger.error(f"failed to create loop overlay: {e}")
    elif getattr(params, 'enable_cta', True):
        try:
            cta_clip = create_cta_clip(params, video_width, video_height, video_clip.duration)
            overlay_clips.append(cta_clip)
            logger.info(f"CTA card added: '{getattr(params, 'cta_text', 'FOLLOW FOR MORE')}'")
        except Exception as e:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(f"CTA overlay failed: {e}") from e
            logger.error(f"failed to create CTA card: {e}")

    if overlay_clips:
        video_clip = CompositeVideoClip([video_clip, *overlay_clips])

    # --- Task 5: BGM with fade-in + lower volume ---
    bgm_file = get_bgm_file(bgm_type=params.bgm_type, bgm_file=params.bgm_file)
    if bgm_file:
        try:
            bgm_vol = getattr(params, 'bgm_volume', 0.12)
            # In seamless-loop mode keep the music continuous (a long fade-out would
            # die at the end then slam back on restart — the loudest "it ended" cue).
            # Loop mode: keep the music continuous across the seam — a 0.15s in/out
            # made a ~0.3s volume dip at the restart. 0.04s only de-clicks the join.
            bgm_fadeout = 0.04 if loop_mode else 3
            bgm_fadein = 0.04 if loop_mode else 1.5
            bgm_clip = AudioFileClip(bgm_file).with_effects(
                [
                    afx.MultiplyVolume(bgm_vol),
                    afx.AudioFadeIn(bgm_fadein),
                    afx.AudioFadeOut(bgm_fadeout),
                    afx.AudioLoop(duration=video_clip.duration),
                ]
            )
            audio_tracks = [audio_clip, bgm_clip]

            # Task 5: SFX whoosh on each image cut
            sfx_dir = os.path.join(utils.root_dir(), "resource", "sfx")
            whoosh_path = os.path.join(sfx_dir, "whoosh.mp3")
            boom_path = os.path.join(sfx_dir, "boom.mp3")
            cut_times_path = os.path.join(output_dir, "cut_times.json")
            sfx_vol = getattr(params, 'sfx_volume', 0.5)

            if getattr(params, 'enable_sfx', True):
                cut_times = []
                if os.path.exists(cut_times_path):
                    try:
                        with open(cut_times_path) as f:
                            cut_times = json.load(f)
                    except Exception:
                        pass
                # Whoosh on each cut (only if the sfx file is present)
                if os.path.exists(whoosh_path):
                    for ct in cut_times:
                        try:
                            sfx = AudioFileClip(whoosh_path).with_effects(
                                [afx.MultiplyVolume(sfx_vol)]
                            ).with_start(ct)
                            audio_tracks.append(sfx)
                        except Exception:
                            pass
                # Impact hit (boom) at t=0 on the hook — independent of whoosh.
                # Suppressed in loop mode: a boom on every restart is a clear "it
                # restarted" marker that breaks the seamless-loop illusion.
                if getattr(params, 'enable_hook_card', True) and os.path.exists(boom_path) and not loop_mode:
                    try:
                        boom = AudioFileClip(boom_path).with_effects(
                            [afx.MultiplyVolume(min(sfx_vol * 1.3, 1.0))]
                        ).with_start(0)
                        audio_tracks.append(boom)
                    except Exception:
                        pass

            audio_clip = CompositeAudioClip(audio_tracks)
        except Exception as e:
            from app.services import one_shot
            if one_shot.is_enabled(params):
                raise one_shot.OneShotError(f"audio polish failed: {e}") from e
            logger.error(f"failed to add bgm/sfx: {str(e)}")

    video_clip = video_clip.with_audio(audio_clip)
    planned_duration = float(video_clip.duration)
    video_clip.write_videofile(
        output_file,
        audio_codec=audio_codec,
        temp_audiofile_path=output_dir,
        threads=params.n_threads or 2,
        logger=None,
        fps=fps,
        codec=video_codec,
        bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        ffmpeg_params=quality_params
    )
    video_clip.close()
    del video_clip
    return planned_duration


def _make_motion_clip(base_clip, effect_idx: int, clip_duration: float, orig_w: int, orig_h: int):
    """
    Apply one of 5 varied Ken Burns motions (Task 2).
    Effect cycles by index so adjacent images never share the same motion.
    Uses ease-out curves for professional deceleration feel.
    """
    d = max(clip_duration, 0.1)

    def ease_out(t):
        p = min(t / d, 1.0)
        return 1.0 - (1.0 - p) ** 2

    def ease_in_out(t):
        p = min(t / d, 1.0)
        return p * p * (3.0 - 2.0 * p)

    effect = effect_idx % 5

    if effect == 0:
        # Zoom in fast (ease-out) 1.0 → 1.22
        zoomed = base_clip.resized(lambda t: 1.0 + 0.22 * ease_out(t))
        return CompositeVideoClip([zoomed.with_position("center")], size=(orig_w, orig_h))

    elif effect == 1:
        # Zoom out (ease-out reversed) 1.22 → 1.0
        zoomed = base_clip.resized(lambda t: 1.22 - 0.22 * ease_out(t))
        return CompositeVideoClip([zoomed.with_position("center")], size=(orig_w, orig_h))

    elif effect == 2:
        # Pan left with slight zoom (scale 1.15, x drifts left)
        scale = 1.15
        ow, oh = int(orig_w * scale), int(orig_h * scale)
        extra_x = ow - orig_w
        extra_y = (oh - orig_h) // 2
        large = base_clip.resized(scale)

        def pan_left(t):
            return (int(-extra_x * ease_out(t)), -extra_y)

        return CompositeVideoClip(
            [large.with_position(pan_left)], size=(orig_w, orig_h)
        )

    elif effect == 3:
        # Pan right with slight zoom (scale 1.15, x drifts right)
        scale = 1.15
        ow, oh = int(orig_w * scale), int(orig_h * scale)
        extra_x = ow - orig_w
        extra_y = (oh - orig_h) // 2
        large = base_clip.resized(scale)

        def pan_right(t):
            return (int(-extra_x + extra_x * ease_out(t)), -extra_y)

        return CompositeVideoClip(
            [large.with_position(pan_right)], size=(orig_w, orig_h)
        )

    else:
        # Zoom in dramatic (ease-in-out) 1.0 → 1.28
        zoomed = base_clip.resized(lambda t: 1.0 + 0.28 * ease_in_out(t))
        return CompositeVideoClip([zoomed.with_position("center")], size=(orig_w, orig_h))


def _apply_grade(im):
    """
    Cinematic color grade: punchier contrast + saturation, a touch of brightness,
    and a soft vignette so raw stock reads as intentionally graded / edited.
    Takes and returns a PIL RGB image.
    """
    from PIL import ImageEnhance, ImageFilter, ImageDraw
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.20)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    # Soft vignette — darken edges ~40% via a blurred elliptical mask.
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    mx, my = int(w * 0.06), int(h * 0.06)
    ImageDraw.Draw(mask).ellipse([mx, my, w - mx, h - my], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.13)))
    darker = Image.blend(im, Image.new("RGB", (w, h), (0, 0, 0)), 0.40)
    return Image.composite(im, darker, mask)


def _make_blurred_background(image_path: str, W: int, H: int) -> str:
    """
    Build a full-frame (W×H) blurred, darkened version of the image to use as a
    background fill, so the foreground image can be shown FULLY (fit, not cropped)
    with no black bars. Returns the path to the saved background jpg.
    """
    from PIL import Image, ImageFilter, ImageEnhance
    img = Image.open(image_path).convert("RGB")
    iw, ih = img.size
    scale = max(W / iw, H / ih)
    bw, bh = int(iw * scale) + 2, int(ih * scale) + 2
    bg = img.resize((bw, bh), Image.LANCZOS)
    left, top = (bw - W) // 2, (bh - H) // 2
    bg = bg.crop((left, top, left + W, top + H))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)
    out = f"{image_path}.bg.jpg"
    bg.save(out, "JPEG", quality=82)
    return out


def preprocess_video(materials: List[MaterialInfo], clip_duration=4, motion_style: str = "varied", _motion_start_index: int = 0, durations: List[float] = None, video_width: int = None, video_height: int = None, fill_mode: str = "cover", color_grade: bool = True, cover_min_keep: float = 0.62):
    motion_counter = _motion_start_index
    for idx, material in enumerate(materials):
        if not material.url:
            continue

        # Per-clip duration (timed sync): each image lasts exactly its caption window.
        this_duration = clip_duration
        if durations and idx < len(durations) and durations[idx]:
            this_duration = max(0.4, float(durations[idx]))

        ext = utils.parse_extension(material.url)
        try:
            clip = VideoFileClip(material.url)
        except Exception:
            clip = ImageClip(material.url)

        width = clip.size[0]
        height = clip.size[1]
        if width < 480 or height < 480:
            logger.warning(f"low resolution material: {width}x{height}, minimum 480x480 required")
            continue

        if ext in const.FILE_TYPE_IMAGES:
            logger.info(f"processing image: {material.url} ({this_duration:.2f}s)")

            if video_width and video_height:
                W, H = video_width, video_height
                from PIL import Image as _PILImage
                with _PILImage.open(material.url) as _im0:
                    iw, ih = _im0.size
                # Decide cover vs blurred-fill PER IMAGE: only crop-to-fill when enough
                # of the image survives, so wide/landscape shots aren't sliced apart.
                cover_scale = max(W / iw, H / ih)
                crop_keep = min(W / (iw * cover_scale), H / (ih * cover_scale))
                use_cover = (fill_mode == "cover") and (crop_keep >= cover_min_keep)

                if use_cover:
                    # ── Full-bleed cover framing ──────────────────────────────
                    # Crop-to-fill the frame, anchored to the upper third so faces/
                    # heads survive. Only used when crop_keep ≥ cover_min_keep.
                    with _PILImage.open(material.url) as _im:
                        im = _im.convert("RGB")
                        nw, nh = max(2, int(iw * cover_scale)), max(2, int(ih * cover_scale))
                        im = im.resize((nw, nh), _PILImage.LANCZOS)
                        left = (nw - W) // 2
                        top = max(0, min(int((nh - H) * 0.30), nh - H))
                        im = im.crop((left, top, left + W, top + H))
                        if color_grade:
                            im = _apply_grade(im)
                        cover_path = f"{material.url}.cover.jpg"
                        im.save(cover_path, "JPEG", quality=90)
                    base = ImageClip(cover_path).with_duration(this_duration)
                    if motion_style != "off":
                        # Zoom-punch: snap-in to 1.10 settling over 0.25s, then a slow
                        # 1.0→1.05 drift — gives each cut energy instead of a flat slide.
                        dd = max(this_duration, 0.1)
                        base = base.resized(
                            lambda t: 1.0 + 0.10 * (1 - min(t / 0.25, 1.0)) + 0.05 * min(t / dd, 1.0)
                        )
                    final_clip = CompositeVideoClip([base.with_position("center")], size=(W, H))
                else:
                    # ── Blurred-fill framing ──────────────────────────────────
                    # Show the WHOLE image (fit, never cropped) over a blurred copy of
                    # itself — used for wide images where cover would cut the subject.
                    # Foreground is graded too so the look stays consistent.
                    fit = min(W / iw, H / ih)
                    fw, fh = max(2, int(iw * fit)), max(2, int(ih * fit))
                    bg_path = _make_blurred_background(material.url, W, H)
                    fg_src = material.url
                    if color_grade:
                        with _PILImage.open(material.url) as _imf:
                            graded = _apply_grade(_imf.convert("RGB"))
                            fg_src = f"{material.url}.graded.jpg"
                            graded.save(fg_src, "JPEG", quality=90)
                    bg_clip = ImageClip(bg_path).with_duration(this_duration)
                    fg = ImageClip(fg_src).with_duration(this_duration).resized(new_size=(fw, fh))
                    if motion_style != "off":
                        fg = fg.resized(lambda t: 1.0 + 0.06 * min(t / max(this_duration, 0.1), 1.0))
                    final_clip = CompositeVideoClip(
                        [bg_clip.with_position("center"), fg.with_position("center")],
                        size=(W, H),
                    )
            else:
                base = ImageClip(material.url).with_duration(this_duration)
                orig_w, orig_h = base.size
                # libx264 rejects odd frame dimensions outright ("height not
                # divisible by 2"); clamp to even before any clip derives its
                # size from this source, since every branch below inherits it.
                even_w, even_h = orig_w - (orig_w % 2), orig_h - (orig_h % 2)
                if (even_w, even_h) != (orig_w, orig_h):
                    base = base.resized(new_size=(even_w, even_h))
                    orig_w, orig_h = even_w, even_h
                if motion_style == "off":
                    final_clip = CompositeVideoClip([base.with_position("center")], size=(orig_w, orig_h))
                elif motion_style == "subtle":
                    zoomed = base.resized(lambda t: 1 + (this_duration * 0.03) * (t / this_duration))
                    final_clip = CompositeVideoClip([zoomed])
                else:
                    final_clip = _make_motion_clip(base, motion_counter, this_duration, orig_w, orig_h)
                    motion_counter += 1

            # Unique output per segment so a reused image keeps its own duration.
            # Written to a _segtmp subdir so temp segments never pollute the
            # shared auto-footage clip cache (they used to be picked up as
            # pool clips on later renders, collapsing variety to 3-4 scenes).
            _seg_dir = os.path.join(os.path.dirname(material.url), "_segtmp")
            os.makedirs(_seg_dir, exist_ok=True)
            _seg_base = os.path.join(_seg_dir, os.path.basename(material.url))
            video_file = f"{_seg_base}.seg{idx}.mp4" if durations else f"{material.url}.mp4"
            final_clip.write_videofile(
                video_file,
                fps=fps,
                logger=None,
                codec=video_codec,
                bitrate=video_bitrate,
                audio_bitrate=audio_bitrate,
                ffmpeg_params=quality_params
            )
            close_clip(final_clip)
            material.url = video_file
            logger.success(f"image processed: {video_file}")

        else:
            # ── Real video clip (e.g. auto-fetched highlight footage) ──────────
            # Trim to the caption window (timed sync) and reframe to 9:16 cover so
            # motion footage is a first-class citizen alongside processed images.
            logger.info(f"processing clip: {material.url} ({this_duration:.2f}s)")
            try:
                src = clip if isinstance(clip, VideoFileClip) else VideoFileClip(material.url)
                src_dur = float(src.duration or this_duration)
                seg_len = max(0.4, min(this_duration, src_dur))
                # Take the segment from the middle of the clip (best action density).
                start = max(0.0, (src_dur - seg_len) / 2.0)
                seg = src.subclipped(start, start + seg_len)

                if video_width and video_height:
                    W, H = video_width, video_height
                    cw, ch = seg.size
                    cr, fr = cw / ch, W / H
                    sf = (H / ch) if cr > fr else (W / cw)
                    nw, nh = max(2, int(cw * sf)), max(2, int(ch * sf))
                    seg = seg.resized(new_size=(nw, nh)).with_position("center")
                    final_clip = CompositeVideoClip([seg], size=(W, H))
                else:
                    final_clip = seg

                _seg_dir = os.path.join(os.path.dirname(material.url), "_segtmp")
                os.makedirs(_seg_dir, exist_ok=True)
                _seg_base = os.path.join(_seg_dir, os.path.basename(material.url))
                video_file = f"{_seg_base}.seg{idx}.mp4" if durations else f"{_seg_base}.proc.mp4"
                final_clip.write_videofile(
                    video_file, fps=fps, logger=None, codec=video_codec,
                    bitrate=video_bitrate, audio_bitrate=audio_bitrate,
                    ffmpeg_params=quality_params,
                )
                close_clip(final_clip)
                material.url = video_file
                logger.success(f"clip processed: {video_file}")
            except Exception as e:
                logger.warning(f"clip processing failed for {material.url}: {e}; passing through")
    return materials

def merge_videos(video_paths: List[str], output_path: str) -> str:
    """Concatenate multiple completed video files into one."""
    logger.info(f"merging {len(video_paths)} videos into {output_path}")
    clips = []
    try:
        for p in video_paths:
            clips.append(VideoFileClip(p))
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )
        logger.success(f"merge complete: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"merge failed: {e}")
        raise
    finally:
        for c in clips:
            try:
                c.close()
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────────────
# COMPARISON / MATCH-CUT PHONK SERIES (additive — only runs when comparison_mode)
# ──────────────────────────────────────────────────────────────────────────────
def _hex_to_rgb(s, default=(255, 255, 255)):
    try:
        s = str(s).lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    except Exception:
        return default


def _find_boom_sfx():
    """Best-effort: locate a short impact SFX in the repo's resources. Returns
    a path or None (SFX is optional — never fail the render over it)."""
    base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "resource",
    )
    for sub in ("sfx", "songs", ""):
        d = os.path.join(base, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            low = f.lower()
            if low.endswith((".mp3", ".wav")) and ("boom" in low or "impact" in low or "hit" in low):
                return os.path.join(d, f)
    return None


def build_comparison_short(task_id, params):
    """
    Build ONE comparison / match-cut phonk short (no voiceover, no subtitles).

    Reads params.comparison_clips (precise YouTube URL + in/out timestamps),
    downloads + cuts each to 9:16, stitches them with a beat-aligned transition,
    overlays bold stat captions, and lays a phonk track whose DROP is aligned to
    the football→comparison cut. Returns the same dict shape as task.start().
    """
    from app.services import auto_footage, beat_sync, one_shot

    aspect = VideoAspect(params.video_aspect)
    video_width, video_height = aspect.to_resolution()
    out_dir = utils.task_dir(task_id)
    os.makedirs(out_dir, exist_ok=True)
    clips_dir = os.path.join(out_dir, "comparison_clips")
    os.makedirs(clips_dir, exist_ok=True)

    specs = params.comparison_clips or []
    if not specs:
        logger.error("comparison_mode: no comparison_clips provided")
        return {"videos": [], "combined_videos": []}

    # 1. Download + cut each exact clip ----------------------------------------
    segments = []  # (path, label, duration)
    for i, spec in enumerate(specs):
        url = spec.get("url", "")
        start = float(spec.get("start", 0.0))
        end = float(spec.get("end", start + 4.0))
        label = spec.get("label", f"clip{i}")
        out_path = os.path.join(clips_dir, f"{i:02d}_{label}.mp4")
        cut = auto_footage.fetch_exact_clip(
            url, start, end, video_width, video_height, out_path,
            max_height=int(getattr(params, "youtube_max_height", 720) or 720),
            fill=spec.get("fill", "cover"),
            retries=0 if one_shot.is_enabled(params) else 3,
        )
        if cut and os.path.exists(cut):
            segments.append({"path": cut, "label": label, "dur": max(0.1, end - start)})
        else:
            logger.warning(f"comparison_mode: clip {i} ({label}) failed to download — skipping")
    if len(segments) < 2:
        logger.error("comparison_mode: need at least 2 usable clips")
        return {"videos": [], "combined_videos": []}

    # 2. Load clips & compute the seam (football→comparison) -------------------
    loaded = []
    for s in segments:
        vc = VideoFileClip(s["path"]).without_audio()
        s["dur"] = float(vc.duration or s["dur"])
        loaded.append(vc)

    # transition_at = explicit, else the end of the first clip (first seam)
    seam = float(getattr(params, "transition_at", 0.0) or 0.0)
    if seam <= 0:
        seam = loaded[0].duration
    total_dur = sum(c.duration for c in loaded)
    cf = float(getattr(params, "crossfade_dur", 0.18) or 0.18)
    style = (getattr(params, "transition_style", "cut") or "cut").lower()

    # 3. Build the seam transition (uniform W×H segments, then concatenate) -----
    built = []
    for i, vc in enumerate(loaded):
        if style == "zoom_punch" and i > 0:
            d = vc.duration
            punched = vc.resized(lambda t: 1.0 + 0.16 * max(0.0, 1.0 - t / max(cf, 0.05)))
            seg = CompositeVideoClip(
                [punched.with_position("center")], size=(video_width, video_height)
            ).with_duration(d)
            built.append(seg)
        else:
            built.append(vc)

    video_clip = None
    if style == "crossfade":
        try:
            from moviepy import vfx
            timeline, t0 = [], 0.0
            for i, seg in enumerate(built):
                if i == 0:
                    timeline.append(seg.with_start(0.0))
                    t0 = seg.duration
                else:
                    s = seg.with_effects([vfx.CrossFadeIn(cf)]).with_start(max(0.0, t0 - cf))
                    timeline.append(s)
                    t0 = (t0 - cf) + seg.duration
            video_clip = CompositeVideoClip(timeline, size=(video_width, video_height))
            total_dur = t0
            seam = loaded[0].duration - cf if seam == loaded[0].duration else seam
        except Exception as e:
            logger.warning(f"comparison_mode: crossfade failed ({e}); using hard cut")
            video_clip = None
    if video_clip is None:
        video_clip = concatenate_videoclips(built, method="chain")
        total_dur = float(video_clip.duration)

    # 4. Beat analysis → align the phonk DROP to the seam ----------------------
    bgm_file = get_bgm_file(bgm_type=getattr(params, "bgm_type", "random"),
                            bgm_file=getattr(params, "bgm_file", ""))
    beats, drop_time = [], 0.0
    bgm_start = float(getattr(params, "bgm_drop_offset", 0.0) or 0.0)
    if bgm_file and os.path.exists(bgm_file) and getattr(params, "beat_sync", True):
        info = beat_sync.analyze(bgm_file)
        beats = info.get("beats", [])
        drop_time = float(info.get("drop_time", 0.0) or 0.0)
        if drop_time > 0:
            bgm_start = max(0.0, drop_time - seam)  # so the drop lands on the seam
            logger.info(f"comparison_mode: drop={drop_time}s seam={seam:.2f}s → bgm_start={bgm_start:.2f}s")
    # Detected beats are in TRACK time; convert to VIDEO time (offset by bgm_start)
    # so caption pops can snap to the beat the viewer actually hears.
    video_beats = sorted(b - bgm_start for b in beats if bgm_start <= b <= bgm_start + total_dur) if beats else []

    # 5. Caption overlays (snap to beats when beat_sync) -----------------------
    font_path = os.path.join(utils.font_dir(), getattr(params, "font_name", "STHeitiMedium.ttc"))
    fsize = int(video_width * 0.075)
    fsize = fsize if fsize % 2 == 0 else fsize + 1
    overlays = []
    for cap in (params.comparison_captions or []):
        text = cap.get("text", "")
        if not text:
            continue
        cstart = float(cap.get("start", 0.0))
        cend = float(cap.get("end", total_dur))
        if getattr(params, "beat_sync", True) and video_beats:
            cstart = beat_sync.nearest_beat(video_beats, cstart)
        cend = min(cend, total_dur)
        if cend <= cstart:
            cend = min(total_dur, cstart + 1.5)
        color = _hex_to_rgb(cap.get("color", "#FFFFFF"))
        y = float(cap.get("y", 0.5))
        emoji = cap.get("emoji", "")
        layer = _render_text_card(
            (text + (" " + emoji if emoji else "")).strip(),
            font_path, fsize, video_width, video_height,
            text_color=color, stroke_color=(0, 0, 0), stroke_width=8,
            y_center_ratio=y, bg_alpha=0,
        )
        dur = cend - cstart
        # Layer is already full-frame W×H; apply pop-in (local time t), centre it,
        # and set the absolute start ONCE (a second with_start would double the
        # offset and push the caption past the end of the video).
        clip = ImageClip(np.array(layer)).with_duration(dur)
        clip = clip.resized(lambda t: 1.0 + 0.12 * (1 - min(t / 0.16, 1)))
        clip = clip.with_position("center").with_start(cstart)
        overlays.append(clip)

    if getattr(params, "loop_follow_tag", False):
        tag = create_follow_tag(params, video_width, video_height, total_dur)
        if tag is not None:
            overlays.append(tag)

    if overlays:
        video_clip = CompositeVideoClip([video_clip, *overlays], size=(video_width, video_height))

    # 6. Audio: phonk BGM (drop-aligned) + optional impact on the drop ---------
    audio_tracks = []
    if bgm_file and os.path.exists(bgm_file):
        try:
            from moviepy import vfx as _vfx  # noqa
        except Exception:
            pass
        try:
            bgm = AudioFileClip(bgm_file)
            seg_end = min(bgm.duration, bgm_start + total_dur)
            bgm = bgm.subclipped(bgm_start, seg_end)
            vol = getattr(params, "bgm_volume", 0.0) or 0.0
            if vol < 0.5:   # music is the LEAD in this format
                vol = 0.95
            bgm = bgm.with_effects([afx.MultiplyVolume(vol), afx.AudioFadeOut(0.4)])
            audio_tracks.append(bgm)
        except Exception as e:
            logger.warning(f"comparison_mode: bgm failed ({e})")

    if getattr(params, "comparison_sfx_on_drop", True):
        boom = _find_boom_sfx()
        if boom:
            try:
                sfx_vol = getattr(params, "sfx_volume", 0.5) or 0.5
                hit = AudioFileClip(boom)
                hit = hit.subclipped(0, min(hit.duration, 1.2)).with_start(max(0.0, seam))
                hit = hit.with_effects([afx.MultiplyVolume(min(1.0, sfx_vol * 1.3))])
                audio_tracks.append(hit)
            except Exception as e:
                logger.warning(f"comparison_mode: sfx failed ({e})")

    if audio_tracks:
        video_clip = video_clip.with_audio(CompositeAudioClip(audio_tracks))

    # 7. Write final-1.mp4 ------------------------------------------------------
    final_path = os.path.join(out_dir, "final-1.mp4")
    logger.info(f"comparison_mode: writing {final_path} ({total_dur:.1f}s, style={style})")
    video_clip.write_videofile(
        final_path,
        audio_codec=audio_codec,
        temp_audiofile_path=out_dir,
        threads=getattr(params, "n_threads", 2) or 2,
        logger=None,
        fps=fps,
        codec=video_codec,
        bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        ffmpeg_params=quality_params,
    )
    try:
        close_clip(video_clip)
        for c in loaded:
            close_clip(c)
    except Exception:
        pass
    logger.success(f"comparison_mode: done → {final_path}")
    return {
        "videos": [final_path],
        "combined_videos": [],
        "script": "",
        "terms": "",
        "materials": [s["path"] for s in segments],
    }

import os
import random
import threading
import time
from typing import List
from urllib.parse import urlencode

import requests
from loguru import logger
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.config import config
from app.models.schema import MaterialInfo, VideoAspect, VideoConcatMode
from app.utils import utils
from app.services import semantic_video

_requested_count = 0
_requested_count_lock = threading.Lock()


def get_api_key(cfg_key: str):
    api_keys = config.app.get(cfg_key)
    if not api_keys:
        raise ValueError(
            f"\n\n##### {cfg_key} is not set #####\n\nPlease set it in the config.toml file: {config.config_file}\n\n"
            f"{utils.to_json(config.app)}"
        )

    # if only one key is provided, return it
    if isinstance(api_keys, str):
        return api_keys

    global _requested_count
    with _requested_count_lock:
        _requested_count += 1
        return api_keys[_requested_count % len(api_keys)]


def search_videos_pexels(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    aspect = VideoAspect(video_aspect)
    video_orientation = aspect.name
    video_width, video_height = aspect.to_resolution()
    api_key = get_api_key("pexels_api_keys")
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    # Build URL
    params = {"query": search_term, "per_page": 20, "orientation": video_orientation}
    query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url,
            headers=headers,
            proxies=config.proxy,
            timeout=(30, 60),
        )
        response = r.json()
        video_items = []
        if "videos" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items
        videos = response["videos"]
        # loop through each video in the result
        for v in videos:
            duration = v["duration"]
            # check if video has desired minimum duration
            if duration < minimum_duration:
                continue
            video_files = v["video_files"]
            # loop through each url to determine the best quality
            for video in video_files:
                w = int(video["width"])
                h = int(video["height"])
                if w == video_width and h == video_height:
                    item = MaterialInfo()
                    item.provider = "pexels"
                    item.url = video["link"]
                    item.duration = duration
                    
                    # Capture image data for similarity comparison
                    if "image" in v:
                        item.thumbnail_url = v["image"]
                    
                    if "video_pictures" in v:
                        item.preview_images = [pic["picture"] for pic in v["video_pictures"]]
                    
                    video_items.append(item)
                    break
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def search_videos_pixabay(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    aspect = VideoAspect(video_aspect)

    video_width, video_height = aspect.to_resolution()

    api_key = get_api_key("pixabay_api_keys")
    # Build URL
    params = {
        "q": search_term,
        "video_type": "all",  # Accepted values: "all", "film", "animation"
        "per_page": 50,
        "key": api_key,
    }
    query_url = f"https://pixabay.com/api/videos/?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url, proxies=config.proxy, timeout=(30, 60)
        )
        response = r.json()
        video_items = []
        if "hits" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items
        videos = response["hits"]
        # loop through each video in the result
        for v in videos:
            duration = v["duration"]
            # check if video has desired minimum duration
            if duration < minimum_duration:
                continue
            video_files = v["videos"]
            # loop through each url to determine the best quality
            for video_type in video_files:
                video = video_files[video_type]
                w = int(video["width"])
                # h = int(video["height"])
                if w >= video_width:
                    item = MaterialInfo()
                    item.provider = "pixabay"
                    item.url = video["url"]
                    item.duration = duration
                    video_items.append(item)
                    break
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def save_video(video_url: str, save_dir: str = "", search_term: str = "", thumbnail_url: str = "", preview_images: list = None) -> str:
    if not save_dir:
        save_dir = utils.storage_dir("cache_videos")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url_without_query = video_url.split("?")[0]
    url_hash = utils.md5(url_without_query)
    video_id = f"vid-{url_hash}"
    video_path = f"{save_dir}/{video_id}.mp4"

    # if video already exists, return the path
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        logger.info(f"video already exists: {video_path}")
        # Save metadata if search_term is provided and metadata doesn't exist
        if search_term and not semantic_video.load_video_metadata(video_path):
            additional_info = {}
            if thumbnail_url:
                additional_info["thumbnail_url"] = thumbnail_url
            if preview_images:
                additional_info["preview_images"] = preview_images
            semantic_video.save_video_metadata(video_path, search_term, additional_info)
        return video_path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # if video does not exist, download it
    with open(video_path, "wb") as f:
        f.write(
            requests.get(
                video_url,
                headers=headers,
                proxies=config.proxy,
                timeout=(60, 240),
            ).content
        )

    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            fps = clip.fps
            clip.close()
            if duration > 0 and fps > 0:
                # Save metadata with search term and image data
                if search_term:
                    additional_info = {}
                    if thumbnail_url:
                        additional_info["thumbnail_url"] = thumbnail_url
                    if preview_images:
                        additional_info["preview_images"] = preview_images
                    semantic_video.save_video_metadata(video_path, search_term, additional_info)
                return video_path
        except Exception as e:
            try:
                os.remove(video_path)
            except Exception:
                pass
            logger.warning(f"invalid video file: {video_path} => {str(e)}")
    return ""


def download_videos(
    task_id: str,
    search_terms: List[str],
    source: str = "pexels",
    video_aspect: VideoAspect = VideoAspect.portrait,
    video_contact_mode: VideoConcatMode = VideoConcatMode.random,
    audio_duration: float = 0.0,
    max_clip_duration: int = 5,
) -> List[str]:
    # Group videos by search term for balanced sampling
    videos_by_term = {}
    found_duration = 0.0
    search_videos = search_videos_pexels
    if source == "pixabay":
        search_videos = search_videos_pixabay

    # Global URL tracking to prevent duplicates across all search terms
    global_video_urls = set()
    
    for search_term in search_terms:
        video_items = search_videos(
            search_term=search_term,
            minimum_duration=max_clip_duration,
            video_aspect=video_aspect,
        )
        logger.info(f"found {len(video_items)} videos for '{search_term}'")

        # Filter out duplicates and associate with search term
        unique_videos = []
        duplicates_removed = 0
        
        for item in video_items:
            # Check for URL duplicates across all search terms
            if item.url not in global_video_urls:
                item.search_term = search_term
                unique_videos.append(item)
                global_video_urls.add(item.url)
                found_duration += item.duration
            else:
                duplicates_removed += 1
        
        if duplicates_removed > 0:
            logger.info(f"removed {duplicates_removed} duplicate URLs for '{search_term}'")
        
        if unique_videos:
            videos_by_term[search_term] = unique_videos

    logger.info(
        f"found videos from {len(videos_by_term)} search terms, total duration: {found_duration} seconds, required: {audio_duration} seconds"
    )
    logger.info(f"total unique video URLs: {len(global_video_urls)}")

    # Create balanced selection from all search terms
    valid_video_items = []
    valid_video_urls = set()
    
    # Round-robin selection from each search term to ensure diversity
    max_videos_per_term = max(1, int(audio_duration / max_clip_duration / len(videos_by_term)) + 1) if videos_by_term else 1
    logger.info(f"targeting max {max_videos_per_term} videos per search term for balanced selection")
    
    # Track selection statistics
    selection_stats = {}
    
    for search_term, videos in videos_by_term.items():
        # Shuffle videos within each search term
        if video_contact_mode.value == VideoConcatMode.random.value:
            random.shuffle(videos)
        
        # Take up to max_videos_per_term from this search term
        count = 0
        for item in videos:
            if item.url not in valid_video_urls and count < max_videos_per_term:
                valid_video_items.append(item)
                valid_video_urls.add(item.url)
                count += 1
        
        selection_stats[search_term] = count
        logger.info(f"selected {count} videos from '{search_term}' ({count}/{len(videos)} available)")
    
    # Final shuffle of the balanced selection
    if video_contact_mode.value == VideoConcatMode.random.value:
        random.shuffle(valid_video_items)
    
    logger.info(f"selected {len(valid_video_items)} videos for download with balanced representation")
    
    # Log diversity metrics
    logger.info("🎯 Diversity metrics:")
    logger.info(f"   📊 Search terms represented: {len(selection_stats)}/{len(search_terms)}")
    for term, count in selection_stats.items():
        percentage = (count / len(valid_video_items)) * 100 if valid_video_items else 0
        logger.info(f"   📹 '{term}': {count} videos ({percentage:.1f}%)")

    video_paths = []
    material_directory = config.app.get("material_directory", "").strip()
    if material_directory == "task":
        material_directory = utils.task_dir(task_id)
    elif material_directory and not os.path.isdir(material_directory):
        material_directory = ""

    total_duration = 0.0
    downloaded_urls = set()  # Track downloaded URLs to prevent runtime duplicates
    
    for item in valid_video_items:
        try:
            # Double-check for URL duplicates at download time
            if item.url in downloaded_urls:
                logger.warning(f"skipping duplicate URL: {item.url}")
                continue
                
            logger.info(f"downloading video: {item.url}")
            # Use the search term associated with this specific video item
            item_search_term = getattr(item, 'search_term', 'unknown')
            saved_video_path = save_video(
                video_url=item.url, save_dir=material_directory, search_term=item_search_term, thumbnail_url=item.thumbnail_url, preview_images=item.preview_images
            )
            if saved_video_path:
                logger.info(f"video saved: {saved_video_path} (search_term: '{item_search_term}')")
                video_paths.append(saved_video_path)
                downloaded_urls.add(item.url)
                seconds = min(max_clip_duration, item.duration)
                total_duration += seconds
                if total_duration > audio_duration:
                    logger.info(
                        f"total duration of downloaded videos: {total_duration} seconds, skip downloading more"
                    )
                    break
        except Exception as e:
            logger.error(f"failed to download video: {utils.to_json(item)} => {str(e)}")
    
    # Final diversity report
    logger.success(f"downloaded {len(video_paths)} videos")
    logger.info(f"🎯 Final diversity: {len(downloaded_urls)} unique URLs downloaded")
    
    return video_paths


def search_images_wikipedia(search_term: str, max_results: int = 10) -> List[MaterialInfo]:
    """Search Wikipedia Commons for free images - no API key required."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_term,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "format": "json",
        "gsrlimit": max_results,
    }
    query_url = f"https://commons.wikimedia.org/w/api.php?{urlencode(params)}"
    logger.info(f"searching Wikipedia Commons: {search_term}")
    wiki_headers = {
        "User-Agent": "MoneyPrinterTurbo/1.2 (https://github.com/DhruvilChauahan0210/MoneyPrinterTurbo-Extended; image-search-feature) python-requests"
    }

    try:
        r = requests.get(query_url, headers=wiki_headers, timeout=(10, 30))
        if not r.text.strip():
            logger.warning(f"Wikipedia Commons returned empty response for '{search_term}'")
            return []
        response = r.json()
        pages = response.get("query", {}).get("pages", {})
        items = []
        for page in pages.values():
            imageinfo = page.get("imageinfo", [])
            if not imageinfo:
                continue
            info = imageinfo[0]
            mime = info.get("mime", "")
            url = info.get("url", "")
            if not url or mime not in ("image/jpeg", "image/png"):
                continue
            item = MaterialInfo()
            item.provider = "wikipedia"
            item.url = url
            item.duration = 5
            item.search_term = search_term
            items.append(item)
        logger.info(f"found {len(items)} images on Wikipedia Commons for '{search_term}'")
        return items
    except Exception as e:
        logger.error(f"Wikipedia Commons search failed: {str(e)}")
        return []


def search_images_duckduckgo(search_term: str, max_results: int = 15) -> List[MaterialInfo]:
    """Search DuckDuckGo Images — free, no API key, broad web coverage."""
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("ddgs/duckduckgo_search not installed, skipping DDG image search")
            return []

    # Stock sites that overlay visible watermarks/credits — skip them so the
    # video doesn't look reused/non-original (which hurts reach + perceived quality).
    WATERMARK_DOMAINS = (
        "gettyimages", "alamy", "shutterstock", "istockphoto", "dreamstime",
        "123rf", "depositphotos", "agefotostock", "picfair", "sportphoto",
        "imago-images", "imago", "stock.adobe", "adobestock", "rexfeatures",
        "shutter", "newscom", "zumapress", "actionimages", "profimedia",
    )

    logger.info(f"searching DuckDuckGo images: {search_term}")
    try:
        results = list(DDGS().images(search_term, max_results=max_results))
        items = []
        skipped = 0
        for r in results:
            url = r.get("image", "")
            if not url:
                continue
            haystack = f"{url} {r.get('source','')} {r.get('url','')}".lower()
            if any(dom in haystack for dom in WATERMARK_DOMAINS):
                skipped += 1
                continue
            item = MaterialInfo()
            item.provider = "duckduckgo"
            item.url = url
            item.duration = 5
            item.search_term = search_term
            items.append(item)
        logger.info(f"found {len(items)} images on DuckDuckGo for '{search_term}' (skipped {skipped} watermarked)")
        return items
    except Exception as e:
        logger.error(f"DuckDuckGo image search failed: {str(e)}")
        return []


def search_images_pexels(search_term: str, max_results: int = 15) -> List[MaterialInfo]:
    """Search Pexels for photos (images, not videos) — reuses existing pexels API key."""
    api_key = get_api_key("pexels_api_keys")
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0",
    }
    params = {"query": search_term, "per_page": max_results}
    query_url = f"https://api.pexels.com/v1/search?{urlencode(params)}"
    logger.info(f"searching Pexels photos: {search_term}")

    try:
        r = requests.get(query_url, headers=headers, proxies=config.proxy, timeout=(10, 30))
        items = []
        for photo in r.json().get("photos", []):
            src = photo.get("src", {})
            url = src.get("large2x") or src.get("large") or src.get("original", "")
            if not url:
                continue
            item = MaterialInfo()
            item.provider = "pexels_photo"
            item.url = url
            item.duration = 5
            item.search_term = search_term
            items.append(item)
        logger.info(f"found {len(items)} photos on Pexels for '{search_term}'")
        return items
    except Exception as e:
        logger.error(f"Pexels photo search failed: {str(e)}")
        return []


def search_images_pixabay(search_term: str, max_results: int = 20) -> List[MaterialInfo]:
    """Search Pixabay for photos (images, not videos) — reuses existing pixabay API key."""
    api_key = get_api_key("pixabay_api_keys")
    params = {
        "key": api_key,
        "q": search_term,
        "image_type": "photo",
        "per_page": max_results,
        "safesearch": "true",
    }
    query_url = f"https://pixabay.com/api/?{urlencode(params)}"
    logger.info(f"searching Pixabay images: {search_term}")

    try:
        r = requests.get(query_url, proxies=config.proxy, timeout=(10, 30))
        response = r.json()
        items = []
        for hit in response.get("hits", []):
            url = hit.get("largeImageURL") or hit.get("webformatURL", "")
            if not url:
                continue
            item = MaterialInfo()
            item.provider = "pixabay_image"
            item.url = url
            item.duration = 5
            item.search_term = search_term
            items.append(item)
        logger.info(f"found {len(items)} images on Pixabay for '{search_term}'")
        return items
    except Exception as e:
        logger.error(f"Pixabay image search failed: {str(e)}")
        return []


def save_image(image_url: str, save_dir: str = "", search_term: str = "") -> str:
    """Download an image, normalize it to RGB JPEG with PIL, and save locally.
    Always outputs a standard JPEG so MoviePy ImageClip never sees exotic formats."""
    from PIL import Image
    import io

    if not save_dir:
        save_dir = utils.storage_dir("cache_images")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url_without_query = image_url.split("?")[0]
    url_hash = utils.md5(url_without_query)
    # Always save as .jpg regardless of source format
    image_path = f"{save_dir}/img-{url_hash}.jpg"

    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
        logger.info(f"image already exists: {image_path}")
        return image_path

    # Wikimedia rate-limits generic browser UAs from scripts — they require a
    # descriptive User-Agent (https://meta.wikimedia.org/wiki/User-Agent_policy)
    if "wikimedia.org" in image_url or "wikipedia.org" in image_url:
        headers = {
            "User-Agent": "MoneyPrinterTurbo/1.2 (https://github.com/DhruvilChauahan0210/MoneyPrinterTurbo-Extended; image-search-feature) python-requests"
        }
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

    try:
        resp = requests.get(image_url, headers=headers, proxies=config.proxy, timeout=(30, 60))
        resp.raise_for_status()

        # Convert to standard RGB JPEG using PIL — handles WebP, CMYK, progressive JPEG, etc.
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        # libx264 requires both dimensions divisible by 2
        w, h = img.size
        new_w = w if w % 2 == 0 else w - 1
        new_h = h if h % 2 == 0 else h - 1
        if new_w != w or new_h != h:
            img = img.crop((0, 0, new_w, new_h))
        img.save(image_path, "JPEG", quality=92)

        if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
            return image_path
    except Exception as e:
        logger.error(f"failed to download/convert image {image_url}: {str(e)}")
        try:
            os.remove(image_path)
        except Exception:
            pass

    return ""


def search_short_clips_pexels(
    search_term: str,
    video_aspect: str = "portrait",
    max_clips: int = 6,
    max_duration: int = 12,
) -> List[MaterialInfo]:
    """Search Pexels for short video clips (≤ max_duration seconds) in portrait orientation."""
    api_key = get_api_key("pexels_api_keys")
    headers = {"Authorization": api_key, "User-Agent": "Mozilla/5.0"}
    params = {
        "query": search_term,
        "per_page": 20,
        "orientation": video_aspect,
    }
    query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
    logger.info(f"searching Pexels short clips: {search_term}")

    try:
        r = requests.get(query_url, headers=headers, proxies=config.proxy, timeout=(10, 30))
        items = []
        for v in r.json().get("videos", []):
            duration = v.get("duration", 999)
            if duration > max_duration:
                continue
            # Pick best-resolution file
            files = sorted(v.get("video_files", []), key=lambda f: f.get("width", 0), reverse=True)
            for vf in files:
                w, h = vf.get("width", 0), vf.get("height", 0)
                if w >= 480 and h >= 480 and vf.get("link"):
                    item = MaterialInfo()
                    item.provider = "pexels_clip"
                    item.url = vf["link"]
                    item.duration = duration
                    item.search_term = search_term
                    items.append(item)
                    break
            if len(items) >= max_clips:
                break
        logger.info(f"found {len(items)} short clips on Pexels for '{search_term}'")
        return items
    except Exception as e:
        logger.error(f"Pexels short clip search failed: {e}")
        return []


def download_images(
    task_id: str,
    search_terms: List[str],
    source: str = "image_search",
    audio_duration: float = 0.0,
    clip_duration: int = 5,
    video_clip_ratio: float = 0.35,
    video_aspect: str = "portrait",
    hook_term: str = "",
) -> List[str]:
    """
    Download images AND short video clips for the given search terms.
    Mixes them so ~video_clip_ratio fraction are real video clips (Pexels Videos)
    and the rest are photos (DDG / Pexels Photos / Wikipedia Commons).
    If hook_term is given, a dedicated search for the exact key moment runs first
    and its results go at the FRONT of the returned list.
    Returns a list of local file paths (.jpg images + .mp4 clips) for preprocess_video().
    """
    all_paths = []
    image_save_dir = utils.storage_dir("cache_images")
    video_save_dir = utils.storage_dir("cache_videos")
    total_duration = 0.0

    # ── Hook moment: dedicated search for the exact key moment ──────────────
    # DDG and Wikipedia are the only sources with real-event photos (stock sites
    # like Pexels won't have e.g. "Zidane headbutt"), so prioritise them here.
    if hook_term:
        logger.info(f"searching for hook moment: '{hook_term}'")
        hook_pool = search_images_duckduckgo(hook_term, max_results=16)
        hook_pool += search_images_wikipedia(hook_term, max_results=4)
        hook_saved = 0
        for item in hook_pool:
            if hook_saved >= 4:
                break
            if item.provider == "wikipedia":
                time.sleep(1.0)
            path = save_image(item.url, save_dir=image_save_dir, search_term=hook_term)
            if path:
                all_paths.append(path)
                total_duration += clip_duration
                hook_saved += 1
                logger.info(f"saved hook candidate: {path} ({item.provider} / '{hook_term}')")
        if not hook_saved:
            logger.warning(f"no hook moment media found for '{hook_term}'")

    # How many clips vs images per term
    clips_per_term = 0 if video_clip_ratio <= 0 else max(1, round(video_clip_ratio * 3))   # e.g. 1-2 clips per term
    images_per_term = max(4, round((1 - video_clip_ratio) * 10))

    # Oversample: gather several times more candidates than the audio strictly
    # needs, so the subject gate + relevance ranker have real choice and can drop
    # weak/off-target images instead of being forced to keep everything.
    candidate_target = max(audio_duration * 4, audio_duration + 30)

    for search_term in search_terms:
        if total_duration >= candidate_target:
            break

        term_paths = []

        # ── Video clips (Pexels Videos) ────────────────────────────────────
        try:
            clip_items = search_short_clips_pexels(
                search_term,
                video_aspect="portrait" if "9:16" in video_aspect or video_aspect == "portrait" else "landscape",
                max_clips=clips_per_term + 2,
            )
            for item in clip_items[:clips_per_term]:
                saved = save_video(
                    video_url=item.url,
                    save_dir=video_save_dir,
                    search_term=search_term,
                )
                if saved:
                    term_paths.append(saved)
                    logger.info(f"saved clip: {saved} (pexels_clip / '{search_term}')")
        except Exception as e:
            logger.warning(f"Pexels clip search skipped: {e}")

        # ── Photos (DDG + Pexels Photos + Wikipedia) ───────────────────────
        ddg_items = search_images_duckduckgo(search_term, max_results=24)

        pexels_photo_items = []
        try:
            pexels_photo_items = search_images_pexels(search_term, max_results=6)
        except Exception as e:
            logger.warning(f"Pexels photo search skipped: {e}")

        wiki_items = search_images_wikipedia(search_term, max_results=4)

        pixabay_items = []
        try:
            pixabay_items = search_images_pixabay(search_term, max_results=6)
        except Exception:
            logger.debug("Pixabay image search skipped (no key configured)")

        photo_pool = ddg_items + pexels_photo_items + wiki_items + pixabay_items
        random.shuffle(photo_pool)

        photos_saved = 0
        for item in photo_pool:
            if photos_saved >= images_per_term:
                break
            if item.provider == "wikipedia":
                time.sleep(1.0)
            path = save_image(item.url, save_dir=image_save_dir, search_term=search_term)
            if path:
                term_paths.append(path)
                photos_saved += 1
                logger.info(f"saved image: {path} ({item.provider} / '{search_term}')")

        # Shuffle clips and photos together per term for variety
        random.shuffle(term_paths)
        for p in term_paths:
            if total_duration >= candidate_target:   # oversample (was: audio_duration)
                break
            all_paths.append(p)
            total_duration += clip_duration

    clips_count = sum(1 for p in all_paths if p.endswith(".mp4"))
    images_count = len(all_paths) - clips_count
    logger.success(
        f"downloaded {len(all_paths)} media items: {clips_count} video clips + {images_count} photos"
    )
    return all_paths


if __name__ == "__main__":
    download_videos(
        "test123", ["Money Exchange Medium"], audio_duration=100, source="pixabay"
    )

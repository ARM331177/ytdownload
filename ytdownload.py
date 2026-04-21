from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

FFMPEG_LOCATION = "/data/data/com.termux/files/usr/bin"

def format_size(bytes_value):
    """Convert bytes to readable format."""
    if not bytes_value:
        return "unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


def get_video_formats(url: str):
    """Get list of available video formats (with quality and size)."""
    with YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])
    video_formats = []

    for f in formats:
        if f.get("vcodec") == "none":
            continue

        ext = f.get("ext")
        if ext not in ("mp4", "webm"):
            continue

        format_id = f.get("format_id")
        height = f.get("height")
        fps = f.get("fps")
        filesize = f.get("filesize") or f.get("filesize_approx")

        quality = f"{height}p" if height else "audio/video"
        if fps:
            quality += f" {fps}fps"

        video_formats.append(
            {
                "format_id": format_id,
                "quality": quality,
                "ext": ext,
                "filesize": filesize,
                "filesize_text": format_size(filesize),
            }
        )

    unique = {}
    for item in video_formats:
        unique[item["format_id"]] = item
    video_formats = list(unique.values())

    def sort_key(x):
        try:
            return int(x["quality"].split("p")[0])
        except Exception:
            return 0

    video_formats.sort(key=sort_key, reverse=True)
    return info, video_formats


def choose_format(video_formats):
    if not video_formats:
        print("Failed to get list of formats.")
        return None

    print("\nAvailable qualities:")
    for i, f in enumerate(video_formats, start=1):
        print(
            f"{i:2d}. {f['quality']:10s} | {f['ext']:4s} | "
            f"размер: {f['filesize_text']}"
        )

    while True:
        choice = input("\nChoose quality number: ").strip()
        if not choice.isdigit():
            print("Enter a number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(video_formats):
            return video_formats[idx]["format_id"]
        print("Invalid number, try again.")


def choose_download_mode():
    print("\nDownload mode:")
    print("1. Video (mp4)")
    print("2. Audio (mp3)")
    while True:
        choice = input("\nChoose mode (1/2): ").strip()
        if choice == "1":
            return "video"
        if choice == "2":
            return "audio"
        print("Invalid choice, enter 1 or 2.")


def download_youtube_video(url: str):
    try:
        info, video_formats = get_video_formats(url)
    except DownloadError as err:
        print("\nFailed to get video information.")
        print(f"Reason: {err}")
        print("\nWhat to try:")
        print("1) Update yt-dlp:  python -m pip install -U yt-dlp")
        print("2) Check if video is available in browser without age/region restrictions.")
        return
    except Exception as err:
        print(f"\nUnexpected error: {err}")
        return

    print(f"\nVideo: {info.get('title', 'no title')}")
    mode = choose_download_mode()
    if mode == "video":
        selected_format_id = choose_format(video_formats)
        if not selected_format_id:
            return
        ydl_opts = {
            "format": f"{selected_format_id}+bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "merge_output_format": "mp4",
        }
    else:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

    print("\nDownloading...")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as err:
        print("\nDownload error.")
        print(f"Reason: {err}")
        print("\nCheck:")
        print("- selected quality;")
        print("- updated yt-dlp;")
        print("- installed ffmpeg (for mp4/mp3 processing).")
        return

    print("Done!")


if __name__ == "__main__":
    link = input("Enter YouTube video link: ").strip()
    download_youtube_video(link)

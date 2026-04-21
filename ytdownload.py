# pip install yt-dlp

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def format_size(bytes_value):
    """Преобразует байты в читаемый вид."""
    if not bytes_value:
        return "неизвестно"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


def get_video_formats(url: str):
    """Получает список доступных видеоформатов (с качеством и размером)."""
    with YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])
    video_formats = []

    for f in formats:
        # Берем форматы, где есть видео-дорожка
        if f.get("vcodec") == "none":
            continue

        # Оставляем только mp4/webm для удобства
        ext = f.get("ext")
        if ext not in ("mp4", "webm"):
            continue

        format_id = f.get("format_id")
        height = f.get("height")
        fps = f.get("fps")
        filesize = f.get("filesize") or f.get("filesize_approx")

        # Текст качества
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

    # Убираем дубли по format_id и сортируем по высоте (сначала лучшее)
    unique = {}
    for item in video_formats:
        unique[item["format_id"]] = item
    video_formats = list(unique.values())

    def sort_key(x):
        # Вытащим число из "1080p"
        try:
            return int(x["quality"].split("p")[0])
        except Exception:
            return 0

    video_formats.sort(key=sort_key, reverse=True)
    return info, video_formats


def choose_format(video_formats):
    if not video_formats:
        print("Не удалось получить список форматов.")
        return None

    print("\nДоступные качества:")
    for i, f in enumerate(video_formats, start=1):
        print(
            f"{i:2d}. {f['quality']:10s} | {f['ext']:4s} | "
            f"размер: {f['filesize_text']}"
        )

    while True:
        choice = input("\nВыбери номер качества: ").strip()
        if not choice.isdigit():
            print("Введи число.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(video_formats):
            return video_formats[idx]["format_id"]
        print("Неверный номер, попробуй снова.")


def choose_download_mode():
    print("\nРежим скачивания:")
    print("1. Видео (mp4)")
    print("2. Аудио (mp3)")
    while True:
        choice = input("\nВыбери режим (1/2): ").strip()
        if choice == "1":
            return "video"
        if choice == "2":
            return "audio"
        print("Неверный выбор, введи 1 или 2.")


def download_youtube_video(url: str):
    try:
        info, video_formats = get_video_formats(url)
    except DownloadError as err:
        print("\nНе удалось получить информацию о видео.")
        print(f"Причина: {err}")
        print("\nЧто попробовать:")
        print("1) Обновить yt-dlp:  python -m pip install -U yt-dlp")
        print("2) Установить JavaScript runtime (рекомендуется Node.js): https://nodejs.org/")
        print("3) Проверить, что видео доступно в браузере без ограничений по возрасту/региону.")
        return
    except Exception as err:
        print(f"\nНеожиданная ошибка: {err}")
        return

    print(f"\nВидео: {info.get('title', 'без названия')}")
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

    print("\nСкачиваю...")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as err:
        print("\nОшибка скачивания.")
        print(f"Причина: {err}")
        print("\nПроверь:")
        print("- выбрано ли существующее качество;")
        print("- обновлен ли yt-dlp;")
        print("- установлен ли ffmpeg (для mp4/mp3 обработки).")
        return

    print("Готово!")


if __name__ == "__main__":
    link = input("Вставь ссылку на YouTube-видео: ").strip()
    download_youtube_video(link)
#!/usr/bin/env python3

import re
import sys
import os
import shutil
import subprocess
import json
from pathlib import Path
from urllib.parse import urlparse

DOWNLOAD_DIR = Path.home() / "Завантажене" / "скачанноемедиа"
VENV_DIR = Path(__file__).resolve().parent / ".venv"
YTDLP_BIN = VENV_DIR / "bin" / "yt-dlp"
SPOTDL_BIN = VENV_DIR / "bin" / "spotdl"

C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_GREEN  = "\033[32m"
C_CYAN   = "\033[36m"
C_RED    = "\033[31m"
C_YELLOW = "\033[33m"
C_DIM    = "\033[2m"

PLATFORM_MAP = {
    "youtube.com":           "YouTube",
    "youtu.be":              "YouTube",
    "m.youtube.com":         "YouTube",
    "youtube-nocookie.com":  "YouTube",
    "music.youtube.com":     "YouTube Music",
    "soundcloud.com":        "SoundCloud",
    "m.soundcloud.com":      "SoundCloud",
    "open.spotify.com":      "Spotify",
    "spotify.com":           "Spotify",
    "tiktok.com":            "TikTok",
    "www.tiktok.com":        "TikTok",
    "instagram.com":         "Instagram",
    "www.instagram.com":     "Instagram",
    "twitter.com":           "Twitter",
    "x.com":                 "Twitter",
    "twitch.tv":             "Twitch",
    "www.twitch.tv":         "Twitch",
    "vimeo.com":             "Vimeo",
    "dailymotion.com":       "Dailymotion",
    "reddit.com":            "Reddit",
    "www.reddit.com":        "Reddit",
    "vk.com":                "VK",
    "rutube.ru":             "Rutube",
    "bandcamp.com":          "Bandcamp",
    "mixcloud.com":          "Mixcloud",
    "bilibili.com":          "Bilibili",
    "ok.ru":                 "OK",
    "facebook.com":          "Facebook",
    "www.facebook.com":      "Facebook",
    "kick.com":              "Kick",
}

PLAYLIST_PLATFORMS = {"SoundCloud", "Spotify", "Bandcamp", "YouTube Music"}

QUALITY_OPTIONS = [
    ("1", "1080p",             "bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
    ("2", "720p",              "bestvideo[height<=720]+bestaudio/best[height<=720]"),
    ("3", "480p",              "bestvideo[height<=480]+bestaudio/best[height<=480]"),
    ("4", "360p",              "bestvideo[height<=360]+bestaudio/best[height<=360]"),
    ("5", "Только аудио (mp3)", "bestaudio/best"),
    ("6", "Лучшее доступное",   "bestvideo+bestaudio/best"),
]


def sanitize_filename(name: str) -> str:
    return "".join(c if c not in '\\/:*?"<>|' else "_" for c in name).strip()


def print_banner():
    print(f"""
{C_BOLD}{C_CYAN}╔══════════════════════════════════════╗
║         ⬇  downl — загрузчик        ║
╚══════════════════════════════════════╝{C_RESET}
{C_DIM}  Папка: {DOWNLOAD_DIR}{C_RESET}
""")


def detect_platform(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower().removeprefix("www.")
    if hostname in PLATFORM_MAP:
        return PLATFORM_MAP[hostname]
    for domain, name in PLATFORM_MAP.items():
        if hostname.endswith("." + domain) or hostname == domain:
            return name
    return "Другое"


def is_youtube(url: str) -> bool:
    return detect_platform(url) in ("YouTube", "YouTube Music")


def is_spotify(url: str) -> bool:
    return detect_platform(url) == "Spotify"


def is_playlist_url(url: str, platform: str) -> bool:
    lower = url.lower()
    if platform == "SoundCloud":
        return "/sets/" in lower
    if platform == "Spotify":
        return "/playlist/" in lower or "/album/" in lower
    if platform == "Bandcamp":
        return "/album/" in lower
    if platform == "YouTube Music":
        return "list=" in lower
    return False


def get_playlist_title(url: str) -> str | None:
    try:
        result = subprocess.run(
            [str(YTDLP_BIN), "--flat-playlist", "-J", "--no-warnings", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            title = data.get("title") or data.get("playlist_title")
            if title:
                return sanitize_filename(title)
    except Exception:
        pass
    return None


def build_output_path(url: str) -> str:
    platform = detect_platform(url)
    base = DOWNLOAD_DIR / platform

    if platform in PLAYLIST_PLATFORMS and is_playlist_url(url, platform):
        playlist_name = get_playlist_title(url)
        if playlist_name:
            print(f"{C_DIM}  📂 Плейлист: {playlist_name}{C_RESET}")
            base = base / playlist_name

    return str(base / "%(title)s.%(ext)s")


def ask_quality() -> tuple[str, bool]:
    print(f"\n{C_BOLD}{C_CYAN}🎬 Выберите качество:{C_RESET}")
    print(f"{C_DIM}{'─' * 40}{C_RESET}")
    for num, label, _ in QUALITY_OPTIONS:
        print(f"  {C_BOLD}{C_CYAN}{num}{C_RESET} │ {label}")
    print(f"{C_DIM}{'─' * 40}{C_RESET}")

    while True:
        try:
            choice = input(f"{C_YELLOW}▸ Ваш выбор [1-6, Enter=6]: {C_RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "6"

        if choice == "":
            choice = "6"

        for num, label, fmt in QUALITY_OPTIONS:
            if choice == num:
                audio_only = (num == "5")
                print(f"{C_GREEN}  ✔ {label}{C_RESET}\n")
                return fmt, audio_only

        print(f"{C_RED}  Неверный ввод, введите число от 1 до 6{C_RESET}")


def format_bytes(b: float | None) -> str:
    if b is None or b < 0:
        return "  ?.? KiB"
    units = ["B", "KiB", "MiB", "GiB"]
    for u in units:
        if b < 1024:
            return f"{b:5.1f} {u}"
        b /= 1024
    return f"{b:5.1f} TiB"


def format_speed(s: float | None) -> str:
    if s is None or s <= 0:
        return "  ?.? KiB/s"
    return format_bytes(s) + "/s"


def format_eta(eta: float | None) -> str:
    if eta is None or eta < 0:
        return "--:--"
    eta = int(eta)
    m, s = divmod(eta, 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def render_pacman_bar(label: str, downloaded: float | None,
                      total: float | None, speed: float | None,
                      eta: float | None, bar_width: int = 25):
    if total and total > 0 and downloaded is not None:
        pct = min(downloaded / total, 1.0)
    else:
        pct = 0.0

    pct_int = int(pct * 100)
    filled = int(pct * bar_width)
    bar = "#" * filled + "-" * (bar_width - filled)

    if len(label) > 20:
        label = label[:18] + ".."
    label = label.ljust(20)

    size_str = format_bytes(downloaded)
    speed_str = format_speed(speed)
    eta_str = format_eta(eta)

    line = f" {C_BOLD}{label}{C_RESET} {size_str}  {speed_str} {eta_str} [{C_BOLD}{C_CYAN}{bar}{C_RESET}] {pct_int:3d}%"
    cols = shutil.get_terminal_size((120, 24)).columns
    print(f"\r{line}".ljust(cols), end="", flush=True)


def make_progress_hook(label: str):
    def hook(d):
        status = d.get("status")
        if status == "downloading":
            render_pacman_bar(
                label=label,
                downloaded=d.get("downloaded_bytes"),
                total=d.get("total_bytes") or d.get("total_bytes_estimate"),
                speed=d.get("speed"),
                eta=d.get("eta"),
            )
        elif status == "finished":
            total = d.get("total_bytes") or d.get("downloaded_bytes") or 0
            render_pacman_bar(
                label=label,
                downloaded=total,
                total=total,
                speed=d.get("speed"),
                eta=0,
            )
            print()
    return hook


def download_spotify(url: str) -> bool:
    print(f"{C_BOLD}{C_CYAN}▶ Скачиваю:{C_RESET}  {url}")
    print(f"{C_DIM}  Площадка: Spotify  🎵 spotdl{C_RESET}")
    print(f"{C_DIM}{'─' * 50}{C_RESET}")

    output_dir = DOWNLOAD_DIR / "Spotify"

    lower = url.lower()
    if "/playlist/" in lower or "/album/" in lower:
        try:
            probe = subprocess.run(
                [str(SPOTDL_BIN), "save", url, "--save-file", "/dev/stderr"],
                capture_output=True, text=True, timeout=60,
            )
            for line in probe.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith(("[", "{")):
                    clean = re.sub(r'\033\[[0-9;]*m', '', line).strip()
                    if clean and "Found" in clean:
                        parts = clean.split(" in ", 1)
                        if len(parts) == 2:
                            folder_name = sanitize_filename(parts[1])
                            if folder_name:
                                output_dir = output_dir / folder_name
                                print(f"{C_DIM}  📂 Плейлист: {folder_name}{C_RESET}")
        except Exception:
            pass

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(SPOTDL_BIN),
        "download", url,
        "--output", str(output_dir / "{title} — {artist}.{output-ext}"),
        "--format", "mp3",
        "--threads", "4",
    ]

    try:
        result = subprocess.run(cmd, cwd=str(output_dir))
        if result.returncode == 0:
            print(f"{C_GREEN}✔ Готово!{C_RESET}\n")
            return True
        else:
            print(f"{C_RED}✖ Ошибка spotdl (код {result.returncode}){C_RESET}\n")
            return False
    except FileNotFoundError:
        print(f"{C_RED}✖ spotdl не найден: {SPOTDL_BIN}{C_RESET}")
        return False
    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}⏸ Загрузка прервана.{C_RESET}")
        return False
    except Exception as e:
        print(f"\n{C_RED}✖ Ошибка: {e}{C_RESET}\n")
        return False


def download(url: str) -> bool:
    if is_spotify(url):
        return download_spotify(url)

    import yt_dlp

    platform = detect_platform(url)
    print(f"{C_BOLD}{C_CYAN}▶ Скачиваю:{C_RESET}  {url}")
    print(f"{C_DIM}  Площадка: {platform}{C_RESET}")
    print(f"{C_DIM}{'─' * 50}{C_RESET}")

    if is_youtube(url):
        fmt, audio_only = ask_quality()
    else:
        fmt = "bestvideo+bestaudio/best"
        audio_only = False

    output_path = build_output_path(url)

    title_label = "Загрузка"
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as probe:
            info = probe.extract_info(url, download=False)
            if info:
                title_label = info.get("title", "Загрузка") or "Загрузка"
    except Exception:
        pass

    ydl_opts = {
        "format": fmt,
        "outtmpl": output_path,
        "writethumbnail": False,
        "postprocessors": [
            {"key": "EmbedThumbnail", "already_have_thumbnail": False},
            {"key": "FFmpegMetadata", "add_metadata": True},
        ],
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "progress_hooks": [make_progress_hook(title_label)],
    }

    if audio_only:
        ydl_opts["postprocessors"].insert(0, {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        })
    else:
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"{C_GREEN}✔ Готово!{C_RESET}\n")
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"\n{C_RED}✖ Ошибка: {e}{C_RESET}\n")
        return False
    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}⏸ Загрузка прервана.{C_RESET}")
        return False
    except Exception as e:
        print(f"\n{C_RED}✖ Ошибка: {e}{C_RESET}\n")
        return False


def main():
    if len(sys.argv) < 2:
        print(f"{C_YELLOW}Использование:{C_RESET} downl <ссылка_1> [ссылка_2 ...]")
        print(f"{C_DIM}Пример: downl https://www.youtube.com/watch?v=dQw4w9WgXcQ{C_RESET}")
        sys.exit(1)

    urls = sys.argv[1:]

    print_banner()
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    fail = 0

    for i, url in enumerate(urls, 1):
        if len(urls) > 1:
            print(f"{C_BOLD}[{i}/{len(urls)}]{C_RESET}")
        if download(url):
            success += 1
        else:
            fail += 1

    if len(urls) > 1:
        print(f"{C_BOLD}{'═' * 50}{C_RESET}")
        print(f"  {C_GREEN}✔ Успешно: {success}{C_RESET}  {C_RED}✖ Ошибок: {fail}{C_RESET}")

    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()

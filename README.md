# downl

Терминальный загрузчик медиа. Одна команда — скачивает видео и музыку с YouTube, SoundCloud, Spotify и 1800+ других сайтов.

## Возможности

- 🎬 **YouTube** — выбор качества (1080p / 720p / 480p / 360p / аудио / лучшее)
- 🎵 **Spotify** — скачивание треков, альбомов и плейлистов через [spotdl](https://github.com/spotDL/spotify-downloader)
- 🎧 **SoundCloud, Bandcamp, Mixcloud** — треки и плейлисты
- 📱 **TikTok, Instagram, Twitter/X, Reddit** — видео из постов
- 📺 **Twitch, Vimeo, Dailymotion, VK, Rutube** — и сотни других
- 📂 **Автосортировка** — файлы раскладываются по папкам площадок
- 📁 **Плейлисты** — сохраняются в подпапки с названием плейлиста
- 📊 **Pacman-style прогресс** — прогресс-бар как при `sudo pacman -S`

## Структура папок

```
~/Завантажене/скачанноемедиа/
├── YouTube/
│   └── Название.mp4
├── SoundCloud/
│   └── Плейлист/
│       └── Трек.mp3
├── Spotify/
│   └── Альбом/
│       └── Трек — Артист.mp3
├── TikTok/
├── Instagram/
└── ...
```

## Установка

### Требования

- Python 3.11+
- ffmpeg

```bash
# Arch
sudo pacman -S python ffmpeg

# Ubuntu / Debian
sudo apt install python3 python3-venv ffmpeg
```

### Установка downl

```bash
git clone https://github.com/stufyyyyn/downl.git
cd downl
chmod +x install.sh
./install.sh
```

Скрипт автоматически:
1. Создаст виртуальное окружение
2. Установит `yt-dlp` и `spotdl`
3. Настроит команду `downl` для вашей оболочки (Fish / Zsh / Bash)

## Использование

```bash
# YouTube
downl https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Spotify
downl https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8
downl https://open.spotify.com/album/...
downl https://open.spotify.com/playlist/...

# SoundCloud
downl https://soundcloud.com/artist/track
downl https://soundcloud.com/artist/sets/playlist

# Несколько ссылок
downl https://youtube.com/watch?v=... https://soundcloud.com/...
```

## Лицензия

MIT

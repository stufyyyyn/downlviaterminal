#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
FISH_FUNC_DIR="$HOME/.config/fish/functions"

echo "╔══════════════════════════════════════╗"
echo "║       ⬇  downl — установка          ║"
echo "╚══════════════════════════════════════╝"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "✖ Python 3 не найден. Установите его и попробуйте снова."
    exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
    echo "⚠ ffmpeg не найден. Для полной функциональности установите ffmpeg."
    echo "  Arch: sudo pacman -S ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo ""
fi

echo "→ Создаю виртуальное окружение..."
python3 -m venv "$VENV_DIR"

echo "→ Устанавливаю зависимости..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet yt-dlp spotdl

echo "→ Настраиваю команду downl..."

SHELL_NAME="$(basename "$SHELL")"

if [ "$SHELL_NAME" = "fish" ]; then
    mkdir -p "$FISH_FUNC_DIR"
    cat > "$FISH_FUNC_DIR/downl.fish" << EOF
function downl --description "Скачивание медиа по ссылке"
    if test (count \$argv) -eq 0
        echo "Использование: downl <ссылка_1> [ссылка_2 ...]"
        return 1
    end
    $VENV_DIR/bin/python $SCRIPT_DIR/downl.py \$argv
end
EOF
    echo "✔ Fish-функция установлена в $FISH_FUNC_DIR/downl.fish"

elif [ "$SHELL_NAME" = "zsh" ]; then
    ALIAS_LINE="alias downl='$VENV_DIR/bin/python $SCRIPT_DIR/downl.py'"
    if ! grep -qF "alias downl=" "$HOME/.zshrc" 2>/dev/null; then
        echo "" >> "$HOME/.zshrc"
        echo "$ALIAS_LINE" >> "$HOME/.zshrc"
    fi
    echo "✔ Алиас добавлен в ~/.zshrc"

elif [ "$SHELL_NAME" = "bash" ]; then
    ALIAS_LINE="alias downl='$VENV_DIR/bin/python $SCRIPT_DIR/downl.py'"
    if ! grep -qF "alias downl=" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "$ALIAS_LINE" >> "$HOME/.bashrc"
    fi
    echo "✔ Алиас добавлен в ~/.bashrc"

else
    echo "⚠ Оболочка $SHELL_NAME не поддерживается автоматически."
    echo "  Добавьте вручную:"
    echo "  alias downl='$VENV_DIR/bin/python $SCRIPT_DIR/downl.py'"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         ✔  Установка завершена!      ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Перезапустите терминал или выполните:"
[ "$SHELL_NAME" = "fish" ] && echo "  exec fish" || echo "  source ~/.${SHELL_NAME}rc"
echo ""
echo "Использование:"
echo "  downl https://www.youtube.com/watch?v=..."
echo "  downl https://open.spotify.com/track/..."
echo "  downl https://soundcloud.com/artist/track"

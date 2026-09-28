#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " PRIVASCOPE Build: Installing native Tesseract OCR       "
echo "=========================================================="

# Check if tesseract binary already exists
if command -v tesseract >/dev/null 2>&1; then
    echo "Tesseract binary already present: $(command -v tesseract)"
    tesseract --version | head -n 1 || true
else
    echo "Tesseract not found in PATH. Detecting installer environment..."

    if [ "$(id -u)" -eq 0 ]; then
        echo "Executing apt-get as root..."
        apt-get update -y && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng
    elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
        echo "Executing apt-get via passwordless sudo..."
        sudo apt-get update -y && sudo apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng
    else
        echo "Non-root build environment without sudo. Unpacking debian packages to ~/.local..."
        INSTALL_DIR="$HOME/.local"
        mkdir -p "$INSTALL_DIR"
        TEMP_DIR="$(mktemp -d)"
        cd "$TEMP_DIR"

        if command -v apt-get >/dev/null 2>&1; then
            apt-get download tesseract-ocr libtesseract5 tesseract-ocr-eng liblept5 2>/dev/null || true
            for deb in *.deb; do
                if [ -f "$deb" ]; then
                    echo "Extracting $deb into $INSTALL_DIR..."
                    dpkg -x "$deb" "$INSTALL_DIR" 2>/dev/null || true
                fi
            done
        fi
        cd - >/dev/null
        rm -rf "$TEMP_DIR"
    fi
fi

echo "=== Verifying Tesseract OCR binary ==="
if command -v tesseract >/dev/null 2>&1; then
    echo "Verified in system PATH: $(command -v tesseract)"
    tesseract --version | head -n 1 || true
elif [ -x "$HOME/.local/usr/bin/tesseract" ]; then
    echo "Verified in user local PATH: $HOME/.local/usr/bin/tesseract"
    "$HOME/.local/usr/bin/tesseract" --version | head -n 1 || true
else
    echo "Notice: Tesseract system binary will be resolved dynamically at runtime."
fi

echo "=== Installing Python production dependencies ==="
pip install --no-cache-dir -r requirements.txt

echo "=========================================================="
echo " PRIVASCOPE Build: Completed successfully                 "
echo "=========================================================="

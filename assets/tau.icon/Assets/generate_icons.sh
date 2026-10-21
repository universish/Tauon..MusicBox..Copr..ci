#!/bin/bash
set -e

# Betiğin çalıştığı konuma göre ana repo dizinini otomatik bul
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ "$SCRIPT_DIR" == *"assets/tau.icon/Assets"* ]]; then
    REPO_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
elif [[ "$SCRIPT_DIR" == *"assets/tau.icon"* ]]; then
    REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
elif [[ "$SCRIPT_DIR" == *"assets"* ]]; then
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    REPO_DIR="$SCRIPT_DIR"
fi

cd "$REPO_DIR"
echo "Çalışma dizini: $REPO_DIR"

# 1. Gerekli araçları kontrol et ve kur
if ! command -v rsvg-convert &> /dev/null || ! command -v magick &> /dev/null; then
    echo "Dönüştürme araçları kuruluyor (librsvg2-tools ve ImageMagick)..."
    sudo dnf install -y librsvg2-tools ImageMagick
fi

ASSETS_DIR="$REPO_DIR/assets/tau.icon/Assets"

if [ ! -d "$ASSETS_DIR" ]; then
    echo "Hata: $ASSETS_DIR klasörü bulunamadı!"
    exit 1
fi

echo ">> 1. SVG katmanları 1024x1024 PNG'ye dönüştürülüyor..."
rsvg-convert -w 1024 -h 1024 -f png "$ASSETS_DIR/01-vinyl-base.svg" -o /tmp/01.png
rsvg-convert -w 1024 -h 1024 -f png "$ASSETS_DIR/02-colour-arcs.svg" -o /tmp/02.png
rsvg-convert -w 1024 -h 1024 -f png "$ASSETS_DIR/03-centre-label.svg" -o /tmp/03.png

echo ">> 2. Katmanlar doğru sırayla birleştiriliyor (Taban -> Yaylar -> Merkez)..."
magick -background none /tmp/01.png /tmp/02.png /tmp/03.png -layers flatten /tmp/tauon-master.png

echo ">> 3. 16x16'dan 512x512'ye kadar tüm PNG boyutları üretiliyor..."
mkdir -p icons

SIZES=(16 24 32 48 64 128 256 512)
for size in "${SIZES[@]}"; do
    magick /tmp/tauon-master.png -resize "${size}x${size}" "icons/tauon-${size}x${size}.png"
    echo "   [✓] icons/tauon-${size}x${size}.png"
done

echo ">> 4. Windows uyumlu çoklu boyutlu .ico dosyası üretiliyor..."
magick icons/tauon-16x16.png icons/tauon-24x24.png icons/tauon-32x32.png \
       icons/tauon-48x48.png icons/tauon-64x64.png icons/tauon-128x128.png \
       icons/tauon-256x256.png icons/tauon.ico
echo "   [✓] icons/tauon.ico"

echo ">> 5. 512x512 ikonu assets ve sources altına kopyalanıyor..."
mkdir -p assets sources
cp icons/tauon-512x512.png assets/tauon-icon.png
cp icons/tauon-512x512.png sources/tauon.png
echo "   [✓] assets/tauon-icon.png ve sources/tauon.png oluşturuldu."

echo ">> 6. icon.json ve geçici dosyalar siliniyor..."
rm -f assets/tau.icon/icon.json
rm -f /tmp/01.png /tmp/02.png /tmp/03.png /tmp/tauon-master.png

echo "İşlem başarıyla tamamlandı!"

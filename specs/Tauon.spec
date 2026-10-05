%global debug_package %{nil}
%global __strip /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}
%global __brp_mangle_shebangs %{nil}
%define _build_id_links none

# check-rpaths ve brp kontrollerini devre dışı bırakır
%global __os_install_post %{nil}
%global __spec_install_post /usr/lib/rpm/check-buildroot

# Dahili kütüphanelerin sistem RPM bağımlılıklarına sızmasını engeller
%global __provides_exclude_from ^/opt/tauon/.*$
%global __requires_exclude_from ^/opt/tauon/.*$

# Dışarıdan makro gelmezse kullanılacak yedek varsayılanlar
%{!?pkg_version: %global pkg_version 12.1.0}
%{!?pkg_release: %global pkg_release 1}

Name:           tauon
Version:        12.1.0
Release:        1%{?dist}
Summary:        A powerful and streamlined music player for the desktop

License:        GPL-3.0-or-later
URL:            https://github.com/Taiko2k/Tauon

Source0:        TauonMusicBox-linux.7z
Source1:        TauonMusicBox-linux-arm64.7z
Source2:        com.Taiko2k.Tauon.metainfo.xml

ExclusiveArch:  x86_64 aarch64

BuildRequires:  7zip
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Grafik, akış kod çözücü ve ses bağımlılıkları
Requires:       SDL3
Requires:       SDL3_image
Requires:       (ffmpeg or ffmpeg-free)
Requires:       mpg123
Requires:       libsamplerate
Requires:       libopenmpt
Requires:       pipewire-pulseaudio
Requires:       pulseaudio-libs
Requires:       python3-websocket-client
Requires:       openssl-libs
Requires:       libwayland-client
Requires:       libwayland-egl
Requires:       libwayland-cursor
Requires:       pipewire-libs
Requires:       hicolor-icon-theme
Requires:       xdg-utils
Requires:       xdg-user-dirs

Provides:       tauonmb = %{version}-%{release}
Provides:       Tauon = %{version}-%{release}
Provides:       TauonMusicBox = %{version}-%{release}

%description
Tauon Music Box is an unofficial repackaging of upstream portable Linux releases.
A powerful and streamlined music player for the desktop featuring gapless playback,
tracker audio support, Jellyfin/Plex streaming, and inline visualization tools.

%prep
%setup -q -c -T
%ifarch x86_64
7z x -snld %{SOURCE0} || :
%endif
%ifarch aarch64
7z x -snld %{SOURCE1} || :
%endif

# Arşiv içeriği tek klasöre açıldıysa kök dizine taşı
if [ $(ls -1A | wc -l) -eq 1 ] && [ -d * ]; then
    SUBDIR=$(ls -1A)
    mv "$SUBDIR"/* . 2>/dev/null || true
    mv "$SUBDIR"/.* . 2>/dev/null || true
    rmdir "$SUBDIR" 2>/dev/null || true
fi

%build
# Portable binary; derleme adımı gerekmez.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/tauon
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/metainfo
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

# Dosyaları /opt/tauon altına yerleştir
cp -a ./* %{buildroot}/opt/tauon/

# 1. Taşınabilir mod dosyasını sil (Veriler ~/.local/share/TauonMusicBox altına yazılsın)
rm -f %{buildroot}/opt/tauon/portable %{buildroot}/opt/tauon/_internal/portable

# 2. Uyumsuz gömülü PipeWire kütüphanesini sil (Fedora'nın yerelini kullansın)
rm -f %{buildroot}/opt/tauon/_internal/libpipewire*

# 3. OpenSSL Sürüm Çakışması Düzeltmesi (ffmpeg subprocess çökmesini engeller)
rm -f %{buildroot}/opt/tauon/_internal/libssl.so*
rm -f %{buildroot}/opt/tauon/_internal/libcrypto.so*
ln -sf %{_libdir}/libssl.so.3 %{buildroot}/opt/tauon/_internal/libssl.so.3
ln -sf %{_libdir}/libcrypto.so.3 %{buildroot}/opt/tauon/_internal/libcrypto.so.3

# 4. Gömülü SDL3 ikilisini silip sisteminkine bağla
rm -f %{buildroot}/opt/tauon/libSDL3.so.0
ln -sf %{_libdir}/libSDL3.so.0 %{buildroot}/opt/tauon/libSDL3.so.0

# Ana ikili dosyaya çalıştırma izni ver
if [ -f "%{buildroot}/opt/tauon/Tauon Music Box" ]; then
    chmod +x "%{buildroot}/opt/tauon/Tauon Music Box"
fi

# /usr/bin/tauon başlatıcı betiği
cat << 'EOF' > %{buildroot}%{_bindir}/tauon
#!/bin/sh
PRELOAD_LIBS=""
for lib in /usr/lib64/libwayland-egl.so.1 /usr/lib64/libSDL3.so.0; do
    if [ -f "$lib" ]; then
        if [ -z "$PRELOAD_LIBS" ]; then
            PRELOAD_LIBS="$lib"
        else
            PRELOAD_LIBS="${PRELOAD_LIBS}:${lib}"
        fi
    fi
done

if [ -n "$PRELOAD_LIBS" ]; then
    export LD_PRELOAD="${PRELOAD_LIBS}${LD_PRELOAD:+:$LD_PRELOAD}"
fi

export SDL_VIDEO_DRIVER="wayland,x11"
export SDL_VIDEODRIVER="wayland,x11"

exec "/opt/tauon/Tauon Music Box" "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/tauon

# Geriye dönük uyumluluk için tauonmb sembolik bağı
ln -sf tauon %{buildroot}%{_bindir}/tauonmb

# Masaüstü kısayolu (StartupWMClass=tauonmb)
cat << 'EOF' > %{buildroot}%{_datadir}/applications/%{name}.desktop
[Desktop Entry]
Name=Tauon Music Box
GenericName=Music Player
Comment=A powerful and streamlined music player for the desktop
Exec=/usr/bin/tauon %U
Icon=tauon
Type=Application
StartupNotify=true
StartupWMClass=tauonmb
Terminal=false
Categories=AudioVideo;Audio;Player;
MimeType=audio/flac;audio/mp3;audio/ogg;audio/wav;audio/x-matroska;audio/m4a;audio/aac;audio/opus;
EOF

# Metainfo kurulumu
install -Dm 644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml

# Simgeleri hicolor dizinlerine yerleştir
find %{buildroot}/opt/tauon -iname "*tauon*.svg" -exec cp -f {} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/tauon.svg \; 2>/dev/null || true
find %{buildroot}/opt/tauon -iname "*tauon*.png" -exec cp -f {} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/tauon.png \; 2>/dev/null || true

if [ ! -f "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps/tauon.svg" ] && [ ! -f "%{buildroot}%{_datadir}/icons/hicolor/256x256/apps/tauon.png" ]; then
    cat << 'EOF' > %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/tauon.svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <defs>
    <linearGradient id="tauonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4a90e2"/>
      <stop offset="100%" stop-color="#8e44ad"/>
    </linearGradient>
  </defs>
  <rect width="128" height="128" rx="28" fill="url(#tauonGrad)"/>
  <circle cx="64" cy="64" r="38" fill="none" stroke="#ffffff" stroke-width="8"/>
  <polygon points="56,46 56,82 82,64" fill="#ffffff"/>
</svg>
EOF
fi

find %{buildroot}%{_datadir}/icons/hicolor -type d -empty -delete 2>/dev/null || true

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml || true

%files
/opt/tauon
%{_bindir}/tauon
%{_bindir}/tauonmb
%{_datadir}/applications/%{name}.desktop
%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml
%{_datadir}/icons/hicolor/*/*/*

%changelog
* Tue Oct 06 2026 Saffet Yavuz : universish <universish@tutamail.com> - %{version}-%{release}
- Automated dynamic release and OpenSSL symlink fixes

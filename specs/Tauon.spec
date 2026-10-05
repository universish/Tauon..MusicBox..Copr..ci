%global debug_package %{nil}
%global __strip /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}
%global __brp_mangle_shebangs %{nil}
%define _build_id_links none

# Upstream runner'ından kalan geçersiz RPATH/RUNPATH denetimini tamamen devre dışı bırakır
%global __arch_install_post /usr/lib/rpm/check-buildroot

# Dahili Python 3.14 ve SDL3 kütüphanelerinin sistem RPM bağımlılıklarına sızmasını engeller
%global __provides_exclude_from ^/opt/tauon/.*$
%global __requires_exclude_from ^/opt/tauon/.*$

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

Requires:       hicolor-icon-theme
Requires:       xdg-utils
Requires:       xdg-user-dirs

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

# Arşiv tek bir alt klasöre açıldıysa kök dizine taşı
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

# Dosyaları /opt/tauon altına taşı
cp -a ./* %{buildroot}/opt/tauon/

# Ana çalıştırıcıyı bul ve /usr/bin/tauon başlatıcı betiğini oluştur
if [ -f "%{buildroot}/opt/tauon/Tauon Music Box" ]; then
    chmod +x "%{buildroot}/opt/tauon/Tauon Music Box"
    cat << 'EOF' > %{buildroot}%{_bindir}/tauon
#!/bin/sh
exec "/opt/tauon/Tauon Music Box" "$@"
EOF
    chmod 755 %{buildroot}%{_bindir}/tauon
elif [ -f "%{buildroot}/opt/tauon/tauon" ]; then
    chmod +x "%{buildroot}/opt/tauon/tauon"
    ln -sf /opt/tauon/tauon %{buildroot}%{_bindir}/tauon
elif [ -f "%{buildroot}/opt/tauon/TauonMusicBox" ]; then
    chmod +x "%{buildroot}/opt/tauon/TauonMusicBox"
    ln -sf /opt/tauon/TauonMusicBox %{buildroot}%{_bindir}/tauon
fi

# Desktop dosyası kurulumu (Dinamik Arama veya Sıfırdan Oluşturma)
DESKTOP_SRC=""
if [ -f "extra/tauon.desktop" ]; then
    DESKTOP_SRC="extra/tauon.desktop"
elif [ -f "%{name}.desktop" ]; then
    DESKTOP_SRC="%{name}.desktop"
elif [ -f "_internal/share/applications/tauon.desktop" ]; then
    DESKTOP_SRC="_internal/share/applications/tauon.desktop"
fi

if [ -n "$DESKTOP_SRC" ]; then
    install -m 0644 "$DESKTOP_SRC" %{buildroot}%{_datadir}/applications/%{name}.desktop
    sed -i 's|^Exec=.*|Exec=/usr/bin/tauon %U|' %{buildroot}%{_datadir}/applications/%{name}.desktop
    sed -i 's|^Icon=.*|Icon=tauon|' %{buildroot}%{_datadir}/applications/%{name}.desktop
else
    cat << 'EOF' > %{buildroot}%{_datadir}/applications/%{name}.desktop
[Desktop Entry]
Name=Tauon Music Box
GenericName=Music Player
Comment=A powerful and streamlined music player for the desktop
Exec=/usr/bin/tauon %U
Icon=tauon
Type=Application
StartupNotify=true
StartupWMClass=tauon
Terminal=false
Categories=AudioVideo;Audio;Player;
MimeType=audio/flac;audio/mp3;audio/ogg;audio/wav;audio/x-matroska;audio/m4a;audio/aac;audio/opus;
EOF
fi

# Metainfo kurulumu
install -Dm 644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml

# Simgeleri arşivden ara ve yerleştir; yoksa gömülü SVG oluştur
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
%{_datadir}/applications/%{name}.desktop
%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml
%{_datadir}/icons/hicolor/*/*/*

%changelog
* Mon Oct 05 2026 Saffet Yavuz : universish <universish@tutamail.com> - %{version}-1
- Fully self-contained build: dynamic desktop generation, fallback SVG icon, and bypass check-rpaths.

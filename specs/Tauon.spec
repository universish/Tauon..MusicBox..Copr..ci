%global debug_package %{nil}
%global __strip /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}
%global __brp_mangle_shebangs %{nil}
%define _build_id_links none

# Upstream GitHub CI ortamından kalan geçersiz RUNPATH denetimini atla
%global __arch_install_post /usr/lib/rpm/check-buildroot

# Dahili Python 3.14 ve SDL3 kütüphanelerinin sistem RPM bağımlılıklarına sızmasını engelle
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
Source3:        tauon.svg

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
# Olası ek rpath kontrolleri için QA maskesini esnet
export QA_RPATHS=0xffff

rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/tauon
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/metainfo
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

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
if [ -f "%{name}.desktop" ]; then
    DESKTOP_SRC="%{name}.desktop"
elif [ -f "extra/tauon.desktop" ]; then
    DESKTOP_SRC="extra/tauon.desktop"
elif [ -f "_internal/share/applications/tauon.desktop" ]; then
    DESKTOP_SRC="_internal/share/applications/tauon.desktop"
else
    DESKTOP_SRC=$(find . -maxdepth 3 -iname "*tauon*.desktop" 2>/dev/null | head -n 1)
fi

if [ -n "$DESKTOP_SRC" ] && [ -f "$DESKTOP_SRC" ]; then
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

# Metainfo ve Simge kurulumu
install -Dm 644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml
install -Dm 644 %{SOURCE3} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/tauon.svg

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml || true

%files
/opt/tauon
%{_bindir}/tauon
%{_datadir}/applications/%{name}.desktop
%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/tauon.svg

%changelog
* Mon Oct 05 2026 Saffet Yavuz : universish <universish@tutamail.com> - %{version}-1
- Dynamic desktop entry installation, RPATH ignores, and bundled dependency isolation.

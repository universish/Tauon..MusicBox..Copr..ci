%global debug_package %{nil}
%global __strip /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}
%global __brp_mangle_shebangs %{nil}
%define _build_id_links none

# Dahili özel kütüphanelerin sistem RPM bağımlılıklarına sızmasını engeller
%global __provides_exclude_from ^/opt/tauon/.*$

Name:           tauon
Version:        12.1.0
Release:        1%{?dist}
Summary:        A powerful and streamlined music player for the desktop

License:        GPL-3.0-or-later
URL:            https://github.com/Taiko2k/Tauon

Source0:        TauonMusicBox-linux.7z
Source1:        TauonMusicBox-linux-arm64.7z
Source2:        com.Taiko2k.Tauon.metainfo.xml
Source3:        tauon.desktop

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
# -snld: Dizin dışına çıkan güvenli sembolik bağlara izin verir
# || : 7-zip'in Humanity simgelerindeki zincirleme bağları atlaması nedeniyle exit code 2 vermesini tolere eder
%ifarch x86_64
7z x -snld %{SOURCE0} || :
%endif
%ifarch aarch64
7z x -snld %{SOURCE1} || :
%endif

# Arşiv içeriği tek bir alt klasör içine açıldıysa kök dizine taşı
if [ $(ls -1A | wc -l) -eq 1 ] && [ -d * ]; then
    SUBDIR=$(ls -1A)
    mv "$SUBDIR"/* . 2>/dev/null || true
    mv "$SUBDIR"/.* . 2>/dev/null || true
    rmdir "$SUBDIR" 2>/dev/null || true
fi

%build
# Önceden derlenmiş binary paketidir; derleme adımı gerekmez.

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

# Ana çalıştırılabilir dosyayı belirle ve /usr/bin/tauon bağlantısını kur
if [ -f %{buildroot}/opt/tauon/tauon ]; then
    chmod +x %{buildroot}/opt/tauon/tauon
    ln -sf /opt/tauon/tauon %{buildroot}%{_bindir}/tauon
elif [ -f %{buildroot}/opt/tauon/tauon.sh ]; then
    chmod +x %{buildroot}/opt/tauon/tauon.sh
    ln -sf /opt/tauon/tauon.sh %{buildroot}%{_bindir}/tauon
elif [ -f %{buildroot}/opt/tauon/TauonMusicBox ]; then
    chmod +x %{buildroot}/opt/tauon/TauonMusicBox
    ln -sf /opt/tauon/TauonMusicBox %{buildroot}%{_bindir}/tauon
fi

# Desktop ve AppStream dosyalarını kur
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE3}
install -Dm 644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml

# Simgeleri hicolor dizinine kopyala
find %{buildroot}/opt/tauon -iname "*tauon*.svg" -exec cp -f {} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/tauon.svg \; 2>/dev/null || true
find %{buildroot}/opt/tauon -iname "*tauon*.png" -exec cp -f {} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/tauon.png \; 2>/dev/null || true

# Boş kalan simge dizinlerini temizle
find %{buildroot}%{_datadir}/icons/hicolor -type d -empty -delete

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/tauon.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml || true

%files
/opt/tauon
%{_bindir}/tauon
%{_datadir}/applications/tauon.desktop
%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml
%{_datadir}/icons/hicolor/*/*/*

%changelog
* Mon Oct 05 2026 universish <universish@users.noreply.github.com> - %{version}-1
- Automatic build from upstream portable release.

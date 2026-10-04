%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs %{nil}
%define _build_id_links none

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
%ifarch x86_64
7z x %{SOURCE0} -oextracted_archive
%endif
%ifarch aarch64
7z x %{SOURCE1} -oextracted_archive
%endif

# Arşiv içi tek bir klasöre açıldıysa kök dizine taşı
if [ $(ls -1 extracted_archive | wc -l) -eq 1 ] && [ -d extracted_archive/* ]; then
    mv extracted_archive/*/* .
    rm -rf extracted_archive
else
    mv extracted_archive/* .
    rm -rf extracted_archive
fi

%build
# Önceden derlenmiş portable binary dosyasıdır; build adımı gerekmez.

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

# Çalıştırılabilir iznini garantile
chmod +x %{buildroot}/opt/tauon/tauon || true

# /usr/bin/tauon linki oluştur
ln -sf /opt/tauon/tauon %{buildroot}%{_bindir}/tauon

# Desktop ve AppStream dosyalarını kur
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE3}
install -Dm 644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml

# Simgeleri hicolor dizinine taşı
find %{buildroot}/opt/tauon -name "*tauon*.svg" -exec cp -f {} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/tauon.svg \; 2>/dev/null || true
find %{buildroot}/opt/tauon -name "*tauon*.png" -exec cp -f {} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/tauon.png \; 2>/dev/null || true

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/tauon.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml || true

%files
/opt/tauon
%{_bindir}/tauon
%{_datadir}/applications/tauon.desktop
%{_datadir}/metainfo/com.Taiko2k.Tauon.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/*

%changelog
* Sun Oct 04 2026 universish <universish@users.noreply.github.com> - %{version}-1
- Automatic build from upstream portable release.
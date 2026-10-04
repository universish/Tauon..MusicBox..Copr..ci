# Tauon MusicBox Copr Packaging CI (`Tauon..MusicBox..Copr..ci`)

Automated continuous integration pipeline to repackage upstream [Tauon MusicBox](https://github.com/Taiko2k/Tauon) prebuilt portable releases into native RPM packages for Fedora Linux, built and hosted on [Fedora Copr](https://copr.fedorainfracloud.org/coprs/universish/Tauon..MusicBox/).

---

## Overview

[Tauon MusicBox](https://github.com/Taiko2k/Tauon) is a modern, streamlined desktop music player designed for music enthusiasts. Upstream distributes pre-compiled standalone portable Linux packages as 7-Zip archives (`x86_64` and `arm64`).

Building complex Python/GTK desktop applications and their dependencies directly inside isolated build environments like Fedora Mock or Copr can be challenging due to offline environment constraints and complex runtime ecosystems. This repository solves that problem by implementing an automated **Portable-7z-to-RPM repackaging pipeline**:

* Monitors upstream GitHub releases for new tags and assets.
* Downloads pre-compiled portable archives for both `x86_64` (`TauonMusicBox-linux.7z`) and `arm64` (`TauonMusicBox-linux-arm64.7z`).
* Extracts and repacks payloads using native Fedora packaging standards.
* Generates a unified Source RPM (`.src.rpm`).
* Dispatches automated build tasks to the `universish/Tauon..MusicBox` Copr repository across `fedora-44` and `fedora-rawhide` chroots.

---

## Features :sparkles:

* Fast, comfortable and responsive UI with beautiful automatic theming.
* Support Milkdrop visualisations.
* Support for **gapless playback**.
* Simple **drag and drop** functionality.
* Supports common codecs such as **.FLAC** and tracker file types such as **.MOD**.
* Seamless support for CUE sheets.
* Stream music from your **PLEX**, **Jellyfin** or **Airsonic** server.
* Customisable UI with multiple widgets to choose from.
* Shortcuts for searching artists on *Rate Your Music* and tracks on *Genius*.
* **Extract archives** and import your music downloads in **one click**! :zap:
* And many more!

---

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── Tauon_ci.yml                   # Automated release detector and Copr trigger
├── sources/
│   ├── com.Taiko2k.Tauon.metainfo.xml     # AppStream catalog metadata
│   └── tauon.desktop                      # Desktop entry configuration
├── specs/
│   └── Tauon.spec                         # RPM packaging specification
└── README.md
└── LICENSE                                     # MIT

```

---

## Component Deep Dive

### 1. GitHub Actions Workflow (`.github/workflows/Tauon_ci.yml`)

The workflow runs on a scheduled cron trigger (daily at 03:00 UTC) and can also be dispatched manually (`workflow_dispatch`).

#### Operational Sequence:

1. **Upstream Release Resolution**: Queries GitHub REST API for `Taiko2k/Tauon` latest release, extracts version tag, and detects whether a new build is required.
2. **Payload Retrieval**: Downloads pre-built portable archives:
* `TauonMusicBox-linux.7z` (`x86_64`)
* `TauonMusicBox-linux-arm64.7z` (`arm64`)


3. **Spec Synchronization**: Automatically bumps the `Version:` field in `specs/Tauon.spec` to match the latest upstream release.
4. **Isolated SRPM Generation**: Uses a clean `fedora:latest` container with `rpmdevtools` and `rpm-build` installed to run `rpmbuild -bs`, generating an authentic `.src.rpm`.
5. **Copr Dispatch (`copr-cli`)**: Configures Copr credentials and initiates non-blocking builds (`copr-cli build --nowait`) targeting the configured chroots on `universish/Tauon..MusicBox`.
6. **Git Tag & State Update**: Commits updated spec metadata and tags the repository with the newly processed release.

---

### 2. RPM Specification (`specs/Tauon.spec`)

The RPM spec file handles payload extraction, architecture switching, filesystem hierarchy standard (FHS) placement, and desktop environment integration.

#### Key Architectural Highlights:

* **Binary Integrity Preservation**:

```spec
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs %{nil}
%define _build_id_links none

```

Disables debuginfo generation and byte-compilation mangling that could break pre-compiled bundled binaries and shared libraries.

* **Multi-Architecture Source Unpacking**:

```spec
%prep
%setup -q -c -T
%ifarch x86_64
7z x %{SOURCE0} -oextracted_archive
%endif
%ifarch aarch64
7z x %{SOURCE1} -oextracted_archive
%endif

```

Selects and extracts the matching portable archive at build time inside Fedora Mock/Copr chroots (`x86_64` vs `aarch64`).

* **FHS Compliance & Desktop Integration**:
* Installs application payloads under `/opt/tauon/`.
* Creates an entry-point symlink at `/usr/bin/tauon -> /opt/tauon/tauon`.
* Installs and validates `tauon.desktop` under `/usr/share/applications/`.
* Installs AppStream metadata under `/usr/share/metainfo/`.
* Extracts and registers HiDPI and scalable icons into `/usr/share/icons/hicolor/`.

---

### 3. AppStream Metadata (`sources/com.Taiko2k.Tauon.metainfo.xml`)

Ensures Tauon integrates natively with graphical software centers (GNOME Software, KDE Discover):

* Validated during `%check` via `appstream-util validate-relax --nonet`.
* Links application identity `com.Taiko2k.Tauon` with categories, upstream repository links, bug tracking, and release metadata.

---

## Configuration & Deployment

### 1. Copr Project Settings

Ensure the destination project exists on Fedora Copr:

* **Project URL**: [https://copr.fedorainfracloud.org/coprs/universish/Tauon..MusicBox/](https://www.google.com/url?sa=E&source=gmail&q=https://copr.fedorainfracloud.org/coprs/universish/Tauon..MusicBox/)
* Navigate to **Settings -> Chroots** and enable:
* `fedora-44-x86_64`
* `fedora-44-aarch64`
* `fedora-rawhide-x86_64`
* `fedora-rawhide-aarch64`

---

## Installation Instructions (Client-Side)

Enable the Copr repository:

```bash
sudo dnf copr enable universish/Tauon..MusicBox

```

Install Tauon MusicBox:

```bash
sudo dnf install tauon

```

Run from terminal or desktop application menu:

```bash
tauon

```

> **Note**: Installing with superuser privileges (`sudo`) is at the user's discretion; no responsibility is accepted for local machine modifications.

---

## Issue Reporting & Bug Tracker

Tauon MusicBox Copr is an unofficial repackaging repository.

* Packaging bugs, spec issues, and Copr build failures should be reported [here](https://github.com/universish/Tauon..MusicBox..Copr..ci/issues).
* Core application bugs, audio playback problems, and feature requests should be reported to the official [Tauon upstream repository](https://github.com/Taiko2k/Tauon/issues).

---

[Tauon MusicBox](https://github.com/Taiko2k/Tauon) is a modern, fast, and streamlined desktop music player designed for playback and collection management.

This repo packages Tauon MusicBox for Fedora by rewrapping the upstream prebuilt Linux portable 7z archives (`TauonMusicBox-linux.7z` and `TauonMusicBox-linux-arm64.7z`) with a Fedora spec. Supports both **x86_64** and **aarch64** architectures, matching the upstream prebuilt release artifacts. A GitHub Actions workflow runs daily at 03:00 UTC to check the latest release from https://github.com/Taiko2k/Tauon and rebuilds COPR only when a new version is published.

The COPR project repository is available from: https://copr.fedorainfracloud.org/coprs/universish/Tauon..MusicBox/

## Features :sparkles:

- Fast, comfortable and responsive UI with beautiful automatic theming.
- Support Milkdrop visualisations.
- Support for **gapless playback**.
- Simple **drag and drop** functionality.
- Supports common codecs such as **.FLAC** and tracker file types such as **.MOD**.
- Seamless support for CUE sheets.
- Stream music from your **PLEX**, **Jellyfin** or **Airsonic** server.
- Customisable UI with multiple widgets to choose from.
- Shortcuts for searching artists on *Rate Your Music* and tracks on *Genius*.
- **Extract archives** and import your music downloads in **one click**! :zap:
- And many more!

---

## Packaging compliance

This package is distributed via COPR only. It rewraps the upstream prebuilt binary archives, so it is **not eligible for the official Fedora repositories**: the Fedora Packaging Guidelines require all binaries to be built from source in the Fedora build system, and this repo intentionally ships the upstream blob as-is (see `specs/Tauon.spec`).

Everything else follows the guidelines:

- `ExclusiveArch: x86_64 aarch64` — matches the tested upstream prebuilt artifacts.
- `%build` present (empty — nothing to compile) so rpm's build hooks run.
- `%check` runs `desktop-file-validate` and `appstream-util validate-relax` on the packaged files inside the build.
- `rpmlint` runs in CI on the built RPM with **0 errors, 0 warnings**: every flagged pattern is inherent to rewrapping the prebuilt portable blob (the `/opt` layout, required `$ORIGIN` runpaths, bare SONAMEs on private libs, unstripped prebuilt binaries, GUI app without man page, doc-free payload) and is filtered in `rpmlintrc` with per-filter rationales.
- `%{_bindir}`, `%{_datadir}`, `%{_metainfodir}` macros used in `%files`.
- License provenance: `License: GPL-3.0-or-later` (SPDX) matches upstream's `LICENSE`.
- `%global debug_package %{nil}` with an explicit rationale: the prebuilt foreign binary cannot produce debuginfo, so the debug package is meaningless for a rewrap. Fedora's `%__os_install_post` gates `brp-strip` and `brp-strip-comment-note` on `%__debug_package` being undefined; disabling this keeps the binary payload intact and byte-identical to upstream.
- The bundled libraries under `/opt/tauon` carry bare SONAMEs. To prevent internal private libraries from leaking into the system package dependency graph, `%__provides_exclude_from` isolates `/opt/tauon`.
- The symlink `/usr/bin/tauon` -> `/opt/tauon/tauon` is declared directly in `%install`, so RPM owns it natively and no scriptlet is needed.
- Upstream ships no dedicated AppStream metadata, so this repo ships a curated `com.Taiko2k.Tauon.metainfo.xml` (RDNS id following standard desktop conventions); desktop file and icons are integrated natively into Fedora's hicolor theme.
- Dependencies: standard dynamic library dependencies are auto-detected by rpmbuild's dependency generator; `hicolor-icon-theme`, `xdg-user-dirs`, and `xdg-utils` are declared explicitly.

---

## License

* Packaging scripts, GitHub Actions CI workflows, and spec files in this repository are licensed under the [MIT License](https://www.google.com/search?q=https://github.com/universish/Tauon..MusicBox..Copr..ci/blob/master/LICENSE)


* Tauon MusicBox is licensed under [GPL-3.0-or-later](https://www.google.com/search?q=https://github.com/Taiko2k/Tauon/blob/master/LICENSE).# Tauon..MusicBox..Copr..ci

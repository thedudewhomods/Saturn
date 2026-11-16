# Saturn for Android

This is an early Android/SDL2 port scaffold for the `legacy` branch. The Android
activity supplies the touch overlay; Saturn's native C/C++ code is built with
the Android NDK through CMake and packaged by Gradle.

## Build from GitHub Actions

1. Obtain your own unmodified US Super Mario 64 ROM dump.
2. Base64-encode it locally:
   - Linux: `base64 -w 0 baserom.us.z64`
   - PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("baserom.us.z64"))`
3. In this repository, open **Settings → Secrets and variables → Actions**.
4. Create a repository secret named `BASEROM_BASE64` and paste the encoded value.
5. Open **Actions → Build Saturn Android APK → Run workflow**.
6. When the build succeeds, download the `Saturn-Android-debug` artifact.

The ROM is copied into the APK and then into the app's private storage because
Saturn extracts its game data from that ROM on first launch. Treat the APK as
private; do not publish or share a build containing your ROM.

## Current status

The Gradle project, SDL2 Android source setup, CMake native target, asset/ROM
bootstrap, and touchscreen controls are present. The GitHub Actions run has
successfully installed the Android SDK/NDK, but native compilation has not yet
been verified: the current run stopped because the `BASEROM_BASE64` secret is
not configured. The first run after adding it will expose any remaining native
port/compiler issues.

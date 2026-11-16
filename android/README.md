# Saturn for Android

This is an early Android/SDL2 port scaffold for the `legacy` branch. The Android
launcher asks for a personal ROM before starting the game. Saturn's native C/C++
code is built with the Android NDK through CMake and packaged by Gradle.

## Build the APK

1. Open **Actions → Build Saturn Android APK**.
2. Select **Run workflow**.
3. When the build succeeds, download the `Saturn-Android-debug` artifact.
4. Install the APK on an Android device.
5. On first launch, choose your own unmodified US Super Mario 64 `.z64` ROM.
   The app checks its size and checksum, then stores it in private app storage.

The ROM is selected on the phone and is **not** embedded in the APK or uploaded
to GitHub Actions. Do not share your ROM file.

## Current status

The Gradle project, SDL2 Android source setup, CMake native target, first-launch
ROM picker, private-storage bootstrap, and touchscreen controls are present.
The GitHub Actions workflow has installed the Android SDK/NDK successfully.
The first native build still needs to complete so any remaining C/C++ port or
asset-generation errors can be fixed.

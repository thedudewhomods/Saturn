import os
import sys
import shutil
import subprocess

def log(phase, message):
    print(f"\n[PHASE: {phase}] {message}")
    print("-" * 60)

def main():
    # ---------------------------------------------------------
    # PHASE A: Host OS Dependency Provisioning
    # ---------------------------------------------------------
    log("A", "Installing System & OpenGL Libraries...")
    try:
        # Added libglu1-mesa-dev to fix the fatal missing GL/glu.h header error
        subprocess.run([
            "sudo", "apt-get", "update", "-y"
        ], check=True)
        subprocess.run([
            "sudo", "apt-get", "install", "-y", 
            "build-essential", "clang", "make", "pkg-config", 
            "libsdl2-dev", "libsdl2-image-dev", "libglu1-mesa-dev"
        ], check=True)
        print("[✓] Host dependencies successfully provisioned.")
    except subprocess.CalledProcessError as e:
        print(f"[X] Dependency installation failed: {e}")
        sys.exit(1)

    # ---------------------------------------------------------
    # PHASE B: Automated Source Code Transformation Engine
    # ---------------------------------------------------------
    log("B", "Patching Engine Code Context Arrays...")

    # Fix 1: Swap GLX Display Targets to Android/SDL2 Context Hooks
    t1 = "src/pc/gfx/gfx_window_manager_api.h"
    if os.path.exists(t1):
        with open(t1, "r", encoding="utf-8", errors="ignore") as f: data = f.read()
        data = data.replace("#define GFX_API_GLX 1", "#define GFX_API_SDL2 1")
        with open(t1, "w", encoding="utf-8") as f: f.write(data)
        print("[✓] Patched window manager API to force SDL2.")

    # Fix 2: Force dynamic mobile resolution scaling matrix
    t2 = "src/pc/gfx/gfx_sdl2.c"
    if os.path.exists(t2):
        with open(t2, "r", encoding="utf-8", errors="ignore") as f: data = f.read()
        find_str = 'window = SDL_CreateWindow("Saturn Studio", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 640, 480, window_flags);'
        replace_str = 'SDL_DisplayMode dm;\n    SDL_GetCurrentDisplayMode(0, &dm);\n    window = SDL_CreateWindow("Saturn Studio", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, dm.w, dm.h, window_flags | SDL_WINDOW_FULLSCREEN);'
        if find_str in data:
            data = data.replace(find_str, replace_str)
            with open(t2, "w", encoding="utf-8") as f: f.write(data)
            print("[✓] Screen aspect configurations mapped to full screen mobile arrays.")

    # Fix 3: Inject On-Screen Virtual Touch Interface directly into the controller loop
    t3 = "src/pc/controller/controller_sdl.c"
    if os.path.exists(t3):
        with open(t3, "r", encoding="utf-8", errors="ignore") as f: data = f.read()
        touch_code = """SDL_PumpEvents();
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_FINGERDOWN || event.type == SDL_FINGERMOTION || event.type == SDL_FINGERUP) {
            float tx = event.tfinger.x; float ty = event.tfinger.y;
            int is_down = (event.type != SDL_FINGERUP);
            if (tx > 0.05 && tx < 0.25 && ty > 0.6 && ty < 0.9) {
                float cx = tx - 0.15; float cy = ty - 0.75;
                if (is_down) {
                    if (cy < -0.04) pad->button |= 0x0008;
                    if (cy > 0.04)  pad->button |= 0x0004;
                    if (cx < -0.04) pad->button |= 0x0002;
                    if (cx > 0.04)  pad->button |= 0x0001;
                }
            }
            if (tx > 0.75 && tx < 0.90 && ty > 0.65 && ty < 0.85) { if (is_down) pad->button |= 0x8000; }
            if (tx > 0.85 && tx < 0.98 && ty > 0.50 && ty < 0.70) { if (is_down) pad->button |= 0x4000; }
            if (tx > 0.02 && tx < 0.15 && ty > 0.10 && ty < 0.25) { if (is_down) pad->button |= 0x2000; }
            if (tx > 0.40 && tx < 0.60 && ty > 0.02 && ty < 0.15) { if (is_down) pad->button |= 0x1000; }
        }
    }"""
        if "SDL_PumpEvents();" in data:
            data = data.replace("SDL_PumpEvents();", touch_code)
            with open(t3, "w", encoding="utf-8") as f: f.write(data)
            print("[✓] Virtual touch input matrix structural overlays successfully bound.")

    # Fix 4: Address file read system layer redirection targets for APK asset delivery streams
    t4 = "src/pc/fs/fs.c"
    if os.path.exists(t4):
        with open(t4, "r", encoding="utf-8", errors="ignore") as f: data = f.read()
        data = data.replace('FILE *f = fopen(path, "rb");', 'SDL_RWops *rw = SDL_RWFromFile(path, "rb");\n    if (!rw) return NULL;')
        with open(t4, "w", encoding="utf-8") as f: f.write(data)
        print("[✓] Rerouted native open routines to internal APK stream operations.")

    # Fix 5: Resolve format-security warnings causing failure states inside the saturn_imgui translation code blocks
    t5 = "src/saturn/imgui/saturn_imgui.cpp"
    if os.path.exists(t5):
        with open(t5, "r", encoding="utf-8", errors="ignore") as f: data = f.read()
        data = data.replace('ImGui::Text(buf);', 'ImGui::Text("%s", buf);')
        data = data.replace('ImGui::Text(anim_name.c_str());', 'ImGui::Text("%s", anim_name.c_str());')
        data = data.replace('ImGui::Text(("Speed: " + std::string(buf)).c_str());', 'ImGui::Text("%s", ("Speed: " + std::string(buf)).c_str());')
        data = data.replace('ImGui::Text((current_model.Expressions[i].Textures[current_model.Expressions[i].CurrentIndex].FileName + " - " + current_model.Expressions[i].Name).c_str());', 'ImGui::Text("%s", (current_model.Expressions[i].Textures[current_model.Expressions[i].CurrentIndex].FileName + " - " + current_model.Expressions[i].Name).c_str());')
        with open(t5, "w", encoding="utf-8") as f: f.write(data)
        print("[✓] Cleaned dynamic string literals syntax bugs inside Saturn ImGui definitions.")

    # ---------------------------------------------------------
    # PHASE C: Android Structural Project Packaging Setup
    # ---------------------------------------------------------
    log("C", "Structuralizing Android Packaging Wrappers...")
    os.makedirs("android_wrapper/app/src/main/jni", exist_ok=True)
    os.makedirs("android_wrapper/app/src/main/res/values", exist_ok=True)
    os.makedirs("android_wrapper/app/src/main/assets", exist_ok=True)

    with open("android_wrapper/app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://android.com" package="com.studio.saturn">
    <uses-feature android:glEsVersion="0x00020000" android:required="true" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <application android:label="Saturn Engine" android:hasCode="true" android:allowBackup="false">
        <activity android:name="org.libsdl.app.SDLActivity" android:exported="true" android:screenOrientation="landscape" android:configChanges="orientation|keyboardHidden|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>''')

    with open("android_wrapper/app/src/main/build.gradle", "w", encoding="utf-8") as f:
        f.write('''plugins { id 'com.android.application' }
android {
    compileSdk 33
    defaultConfig {
        applicationId "com.studio.saturn"
        minSdk 21
        targetSdk 33
        versionCode 1
        versionName "1.0"
        ndk { abiFilters 'arm64-v8a', 'armeabi-v7a' }
    }
    externalNativeBuild { ndkBuild { path "src/main/jni/Android.mk" } }
}''')

    with open("android_wrapper/settings.gradle", "w", encoding="utf-8") as f:
        f.write("include ':app'\n")

    with open("android_wrapper/app/src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
        f.write('<resources><string name="app_name">Saturn Engine</string></resources>')

    with open("android_wrapper/app/src/main/jni/Android.mk", "w", encoding="utf-8") as f:
        f.write('''LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := main
LOCAL_SRC_FILES := $(wildcard $(LOCAL_PATH)/../../../../src/**/*.c) \\
                   $(wildcard $(LOCAL_PATH)/../../../../src/**/*.cpp)
LOCAL_LDLIBS := -lGLESv2 -lEGL -llog -landroid -lGLU
LOCAL_SHARED_LIBRARIES := SDL2 SDL2_image
include $(BUILD_SHARED_LIBRARY)''')

    print("[✓] Packaging templates generated successfully.")

if __name__ == "__main__":
    main()

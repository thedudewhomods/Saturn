import os
import sys
import shutil
import subprocess

# Secure dependency validation checks
try:
    import yaml
except ImportError:
    print("[*] Dependency missing. Provisioning PyYAML automatically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

def log_phase(name):
    print(f"\n========================================================")
    print(f" >>> PHASE: {name}")
    print(f"========================================================")

def detect_environment():
    if os.path.exists("/data/data/com.termux"):
        return "termux"
    elif os.path.exists("/usr/bin/apt") or os.path.exists("/etc/debian_version"):
        return "ubuntu"
    else:
        return "unknown"

def setup_dependencies(env):
    log_phase("A - Dependency Provisioning & Architecture Selection")
    print(f"[*] Target runtime context evaluated: System={env.upper()}")
    
    if env == "termux":
        cmds = [
            "pkg update -y",
            "pkg install git clang make python pkg-config libandroid-support SDL2 SDL2-image openjdk-17 -y"
        ]
    elif env == "ubuntu":
        cmds = [
            "sudo apt-get update -y",
            "sudo apt-get install -y git build-essential clang make python3 pkg-config libsdl2-dev libsdl2-image-dev openjdk-17-jdk gradle"
        ]
    else:
        print("[!] Unsupported operating environment. Proceeding with caution...")
        return

    for cmd in cmds:
        print(f"[*] Executing pipeline command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

def verify_workspace_assets(rom_name):
    print(f"[*] Searching for asset baseline dependency: '{rom_name}'")
    if not os.path.exists(rom_name):
        print(f"\n[X] CRITICAL ERROR: Reference asset verification failed!")
        print(f"    You must supply a valid Super Mario 64 US ROM to extract assets.")
        print(f"    Drop '{rom_name}' into this directory and rerun.\n")
        sys.exit(1)
    print(f"[✓] Asset token verified: Located path target -> {os.path.abspath(rom_name)}")

def clone_repository(url):
    target_dir = "Saturn_Source"
    if os.path.exists(target_dir):
        print(f"[*] Source infrastructure folder '{target_dir}' discovered. Cleaning dynamic caches...")
        return target_dir
    print(f"[*] Fetching target codebase repository: {url}")
    subprocess.run(["git", "clone", url, target_dir], check=True)
    return target_dir

def run_patch_engine(repo_path, patches):
    log_phase("B - Code Transformation & Native Architecture Mapping")
    for index, patch in enumerate(patches):
        action = patch.get("action")
        target = os.path.join(repo_path, patch.get("target"))
        print(f"[*] Processing patch index [{index}] -> Action: {action} on Target: {patch.get('target')}")

        if action == "replace_string":
            if not os.path.exists(target):
                print(f"[!] Warning: File target not matching repository tree structure: {target}")
                continue
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
            
            find_val = patch.get("find")
            replace_val = patch.get("replace")
            
            if find_val in data:
                data = data.replace(find_val, replace_val)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(data)
                print(f"    [✓] Transformation mapping injected successfully.")
            else:
                print(f"    [!] Target signature token omitted (already patched or absent).")

        elif action == "create_file":
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(patch.get("content", ""))
            print(f"    [✓] Dynamic file resource compiled down to target.")

def structuralize_android_wrapper(repo_path, config):
    log_phase("C.1 - Android Project Structure Generator")
    
    # Establish complete project directories
    base_app_dir = os.path.join(repo_path, "android_wrapper")
    jni_dir = os.path.join(base_app_dir, config["android_target"]["jni_dir"])
    res_dir = os.path.join(base_app_dir, "app/src/main/res/values")
    
    os.makedirs(jni_dir, exist_ok=True)
    os.makedirs(res_dir, exist_ok=True)

    # 1. Generate Manifest
    manifest_file = os.path.join(base_app_dir, config["android_target"]["manifest_path"])
    os.makedirs(os.path.dirname(manifest_file), exist_ok=True)
    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://android.com" package="com.studio.saturn">
    <uses-feature android:glEsVersion="0x00020000" android:required="true" />
    <application android:label="Saturn Engine" android:hasCode="true" android:allowBackup="false">
        <activity android:name="org.libsdl.app.SDLActivity" android:exported="true" android:screenOrientation="landscape">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>''')

    # 2. Generate Build Gradle
    gradle_file = os.path.join(base_app_dir, config["android_target"]["gradle_path"])
    os.makedirs(os.path.dirname(gradle_file), exist_ok=True)
    with open(gradle_file, "w", encoding="utf-8") as f:
        f.write('''plugins {
    id 'com.android.application'
}
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
    buildTypes {
        release {
            minifyEnabled false
        }
    }
    externalNativeBuild {
        ndkBuild {
            path "src/main/jni/Android.mk"
        }
    }
}''')

    # 3. Generate Settings Gradle
    settings_file = os.path.join(base_app_dir, config["android_target"]["settings_path"])
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write("include ':app'\n")

    # 4. Generate Strings Value Resource XML
    with open(os.path.join(res_dir, "strings.xml"), "w", encoding="utf-8") as f:
        f.write('<resources><string name="app_name">Saturn Engine</string></resources>')

    print("[✓] Scaffolding tree built out. Native links mapped to pipeline assets.")
    return base_app_dir

def package_and_compile(repo_path, wrapper_path, rom_name):
    log_phase("C.2 - Native Cross-Compilation & Gradle Build Pipeline")
    
    # Relocate raw file dependencies directly inside targeted source location
    dest_rom_path = os.path.join(repo_path, rom_name)
    if not os.path.exists(dest_rom_path):
        shutil.copy(rom_name, dest_rom_path)
    
    original_cwd = os.getcwd()
    os.chdir(repo_path)
    
    try:
        print("[*] Generating game source native binary dependencies via system make blocks...")
        # Step 1: Run native resource compilation
        subprocess.run(["make", "TARGET_ANDROID=1", "clean"], check=True)
        # We run the build asset extractor engine step natively
        subprocess.run(["make", "TARGET_ANDROID=1", "-j4"], check=True)
        
        # Step 2: Switch execution target down into our wrapper stack context to run gradle targets
        os.chdir(os.path.join(original_cwd, wrapper_path))
        print("[*] Running Gradle asset packaging system framework...")
        
        # Check for local gradle setup or execute global system wrapper variables
        gradle_cmd = "./gradlew" if os.path.exists("gradlew") else "gradle"
        subprocess.run([gradle_cmd, "assembleDebug"], check=True)
        
        # Step 3: Discover target outputs context and sweep back home
        output_apk = os.path.join("app/build/outputs/apk/debug/app-debug.apk")
        if os.path.exists(output_apk):
            final_target = os.path.join(original_cwd, "Saturn_Engine_Target.apk")
            shutil.copy(output_apk, final_target)
            print(f"\n[✓][✓][✓] SUCCESS Pipeline execution target hit!")
            print(f"          Output package written to: {final_target}\n")
        else:
            print("[X] Pipeline execution failure: Compilation occurred but binary signature skipped output targets.")
            
    except subprocess.CalledProcessError as err:
        print(f"[X] Execution failed inside internal sub-process block. Code details: {err}")
        sys.exit(1)
    finally:
        os.chdir(original_cwd)

def main():
    if not os.path.exists("build_config.yml"):
        print("[X] Configuration sequence failure: 'build_config.yml' manifest must occupy the running workspace.")
        sys.exit(1)

    with open("build_config.yml", "r", encoding="utf-8") as file_stream:
        config = yaml.safe_load(file_stream)

    env_type = detect_environment()
    setup_dependencies(env_type)
    verify_workspace_assets(config["project"]["rom_name"])
    
    repo_directory = clone_repository(config["project"]["repo_url"])
    
    # Process patches
    run_patch_engine(repo_directory, config["patch_sequence"])
    
    # Construct runtime directories and compile components
    wrapper_path = structuralize_android_wrapper(repo_directory, config)
    package_and_compile(repo_directory, wrapper_path, config["project"]["rom_name"])

if __name__ == "__main__":
    main()

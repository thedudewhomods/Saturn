import os
import sys
import shutil
import subprocess

try:
    import yaml
except ImportError:
    print("[*] Installing PyYAML dependency...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

def detect_environment():
    if os.path.exists("/data/data/com.termux"):
        return "termux"
    elif os.path.exists("/usr/bin/apt"):
        return "ubuntu"
    else:
        return "unknown"

def setup_dependencies(env):
    print(f"[*] Environment detected: {env}")
    if env == "termux":
        cmds = [
            "pkg update -y",
            "pkg upgrade -y",
            "pkg install git clang make python pkg-config libandroid-support SDL2 SDL2-gfx SDL2-image libusb -y"
        ]
    elif env == "ubuntu":
        cmds = [
            "sudo apt-get update -y",
            "sudo apt-get install -y git build-essential clang make python3 pkg-config libsdl2-dev libsdl2-image-dev openjdk-17-jdk-headless"
        ]
    else:
        print("[!] Unsupported operating system environment.")
        sys.exit(1)

    for cmd in cmds:
        print(f"[*] Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

def clone_repo(repo_url):
    repo_name = "Saturn"
    if os.path.exists(repo_name):
        print(f"[*] Repository directory '{repo_name}' already exists. Skipping clone.")
        return repo_name
    
    print(f"[*] Cloning repository from {repo_url}...")
    subprocess.run(["git", "clone", repo_url, repo_name], check=True)
    return repo_name

def execute_patches(repo_path, patches):
    print("[*] Beginning code-level modification engine...")
    for patch in patches:
        action = patch.get("action")
        target = os.path.join(repo_path, patch.get("target"))

        if action == "delete":
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
                print(f"[✓] Deleted: {target}")
            else:
                print(f"[!] Target not found for deletion: {target}")

        elif action == "replace_string":
            if not os.path.exists(target):
                print(f"[X] Error: Target file missing for replacement: {target}")
                sys.exit(1)
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            find_str = patch.get("find")
            replace_str = patch.get("replace")
            
            if find_str in content:
                content = content.replace(find_str, replace_str)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[✓] Modified: {target}")
            else:
                print(f"[!] Warning: String match not found in {target}")

        elif action == "create_file":
            parent_dir = os.path.dirname(target)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(patch.get("content", ""))
            print(f"[✓] Created: {target}")

def verify_rom(repo_path, rom_name):
    expected_rom_path = os.path.join(repo_path, rom_name)
    current_dir_rom = os.path.join(".", rom_name)

    if os.path.exists(current_dir_rom) and not os.path.exists(expected_rom_path):
        shutil.copy(current_dir_rom, expected_rom_path)

    if not os.path.exists(expected_rom_path):
        print(f"\n[X] CRITICAL ERROR: Asset validation failed.")
        print(f"    Please place your Super Mario 64 US ROM inside the workspace.")
        print(f"    Expected path: {os.path.abspath(expected_rom_path)}\n")
        sys.exit(1)
    print(f"[✓] Verified ROM asset asset base found: {expected_rom_path}")

def run_compiler(repo_path):
    print("[*] Launching cross-compilation pipeline...")
    original_dir = os.getcwd()
    os.chdir(repo_path)
    try:
        subprocess.run(["make", "clean"], check=True)
        subprocess.run(["make", "TARGET_ANDROID=1", "-j4"], check=True)
        print("[✓] Native engine binary compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[X] Compilation sequence aborted with error code {e.returncode}")
        sys.exit(1)
    finally:
        os.chdir(original_dir)

def main():
    if not os.path.exists("build_config.yml"):
        print("[X] Error: Configuration asset 'build_config.yml' is missing.")
        sys.exit(1)

    with open("build_config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    env = detect_environment()
    setup_dependencies(env)
    
    repo_path = clone_repo(config["project"]["repo_url"])
    verify_rom(repo_path, config["project"]["rom_name"])
    
    execute_patches(repo_path, config["patch_sequence"])
    run_compiler(repo_path)

if __name__ == "__main__":
    main()

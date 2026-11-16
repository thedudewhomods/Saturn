#!/usr/bin/env python3
"""Prepare Saturn's Android build inputs. This does not pretend to compile the game."""
from __future__ import annotations
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android"
SDL = ANDROID / "SDL"

def run(args: list[str], cwd: pathlib.Path = ROOT) -> None:
    print("+", " ".join(map(str, args)), flush=True)
    subprocess.run(args, cwd=cwd, check=True)

def main() -> int:
    required = [
        ROOT / "Makefile",
        ROOT / "Makefile.split",
        ROOT / "src/pc/pc_main.c",
        ROOT / "src/pc/controller/controller_sdl2.c",
        ANDROID / "settings.gradle",
        ANDROID / "app/build.gradle",
        ANDROID / "app/src/main/cpp/CMakeLists.txt",
        ANDROID / "app/src/main/AndroidManifest.xml",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        print("Android preflight failed; missing required project files:", *missing, sep="\n  ", file=sys.stderr)
        return 2

    if not SDL.is_dir():
        run(["git", "clone", "--depth", "1", "--branch", "release-2.30.11",
             "https://github.com/libsdl-org/SDL.git", str(SDL)])
    if not (SDL / "CMakeLists.txt").is_file():
        print("SDL checkout exists but is incomplete: android/SDL/CMakeLists.txt is missing.", file=sys.stderr)
        return 3

    # The project relies on a legally obtained US ROM dump for asset extraction.
    rom = ROOT / "baserom.us.z64"
    if not rom.is_file():
        print("Missing baserom.us.z64. Add your own legally obtained US ROM as the BASEROM_BASE64 GitHub Actions secret.", file=sys.stderr)
        return 4

    run(["make", "-C", "tools", "-j2"])
    run([sys.executable, "extract_assets.py", "us"])
    assets = ANDROID / "app/src/main/assets"
    assets.mkdir(parents=True, exist_ok=True)
    for folder in ("res", "fonts"):
        source = ROOT / folder
        if source.exists():
            target = assets / folder
            if target.exists():
                import shutil
                shutil.rmtree(target)
            import shutil
            shutil.copytree(source, target)
    print("Android preflight completed. Native compilation is performed by Gradle/CMake.", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

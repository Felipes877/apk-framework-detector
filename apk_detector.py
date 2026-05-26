#!/usr/bin/env python3
import os
import sys
import shutil
import tempfile
import subprocess
import argparse
from pathlib import Path

class Colors:
    HEADER = "\033[95m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def cprint(msg, color=Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")

def get_apktool_cmd() -> str:
    if sys.platform == "win32":
        return "apktool.bat"
    return "apktool"


def run_apktool(apk_path: str, output_dir: str) -> bool:
    cmd = get_apktool_cmd()
    cprint(f"\n[*] Running {cmd} ...", Colors.CYAN)
    try:
        result = subprocess.run(
            [cmd, "d", apk_path, "-o", output_dir, "-f"],
            stdin=subprocess.DEVNULL,   
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            cprint(f"[!] apktool returned an error:\n{result.stderr}", Colors.RED)
            return False
        cprint("[+] apktool finished successfully ✓", Colors.GREEN)
        return True
    except FileNotFoundError:
        cprint(f"[✗] '{cmd}' is not installed or not found on PATH!", Colors.RED)
        if sys.platform == "win32":
            cprint("    Download apktool.bat from: https://apktool.org", Colors.YELLOW)
        else:
            cprint("    Install via: sudo apt install apktool  (or brew install apktool on Mac)", Colors.YELLOW)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        cprint("[✗] apktool timed out!", Colors.RED)
        return False

def file_exists(base: Path, *rel_parts) -> bool:
    return (base / Path(*rel_parts)).is_file()


def dir_exists(base: Path, *rel_parts) -> bool:
    return (base / Path(*rel_parts)).is_dir()


def find_files(base: Path, pattern: str) -> list:
    return list(base.rglob(pattern))

def find_in_lib(base: Path, filename: str) -> bool:
    lib_dir = base / "lib"
    if not lib_dir.is_dir():
        return False
    return any(lib_dir.rglob(filename))

def detect_flutter(base: Path) -> tuple[bool, list]:
    evidence = []
    if find_in_lib(base, "libflutter.so"):
        evidence.append("Found libflutter.so in lib/")
    if find_in_lib(base, "libapp.so"):
        evidence.append("Found libapp.so in lib/")
    if dir_exists(base, "assets", "flutter_assets"):
        evidence.append("Found assets/flutter_assets/")
    if file_exists(base, "assets", "flutter_assets", "AssetManifest.json"):
        evidence.append("Found assets/flutter_assets/AssetManifest.json")
    return len(evidence) > 0, evidence


def detect_react_native(base: Path) -> tuple[bool, list]:
    evidence = []
    if file_exists(base, "assets", "index.android.bundle"):
        evidence.append("Found assets/index.android.bundle")
    if find_in_lib(base, "libreactnativejni.so"):
        evidence.append("Found libreactnativejni.so in lib/")
    if find_in_lib(base, "libjsc.so"):
        evidence.append("Found libjsc.so in lib/")
    if dir_exists(base, "assets", "node_modules"):
        evidence.append("Found assets/node_modules/")
    return len(evidence) > 0, evidence


def detect_unity(base: Path) -> tuple[bool, list]:
    evidence = []
    if find_in_lib(base, "libunity.so"):
        evidence.append("Found libunity.so in lib/")
    if find_in_lib(base, "libil2cpp.so"):
        evidence.append("Found libil2cpp.so in lib/")
    if find_in_lib(base, "libmono.so"):
        evidence.append("Found libmono.so in lib/")
    if dir_exists(base, "assets", "bin", "Data"):
        evidence.append("Found assets/bin/Data/")
    return len(evidence) > 0, evidence


def detect_xamarin(base: Path) -> tuple[bool, list]:
    evidence = []
    if find_in_lib(base, "libmonodroid.so"):
        evidence.append("Found libmonodroid.so in lib/")
    if find_in_lib(base, "libxamarin-app.so"):
        evidence.append("Found libxamarin-app.so in lib/")
    dll_files = find_files(base / "assets" if (base / "assets").is_dir() else base, "*.dll")
    if dll_files:
        evidence.append(f"Found {len(dll_files)} .dll file(s) in assets/assemblies/")
    return len(evidence) > 0, evidence


def detect_cordova(base: Path) -> tuple[bool, list]:
    evidence = []
    has_www     = dir_exists(base, "assets", "www")
    has_cordova = file_exists(base, "assets", "www", "cordova.js")
    has_plugins = file_exists(base, "assets", "www", "cordova_plugins.js")
    has_index   = file_exists(base, "assets", "www", "index.html")

    if has_www:
        evidence.append("Found assets/www/")
    if has_cordova:
        evidence.append("Found assets/www/cordova.js")
    if has_plugins:
        evidence.append("Found assets/www/cordova_plugins.js")
    if has_index:
        evidence.append("Found assets/www/index.html")

    detected = has_www and (has_cordova or has_plugins)
    return detected, evidence


def detect_capacitor(base: Path) -> tuple[bool, list]:
    evidence = []
    has_public  = dir_exists(base, "assets", "public")
    has_config  = file_exists(base, "assets", "capacitor.config.json")
    has_plugins = file_exists(base, "assets", "capacitor.plugins.json")
    has_index   = file_exists(base, "assets", "public", "index.html")

    if has_public:
        evidence.append("Found assets/public/")
    if has_config:
        evidence.append("Found assets/capacitor.config.json")
    if has_plugins:
        evidence.append("Found assets/capacitor.plugins.json")
    if has_index:
        evidence.append("Found assets/public/index.html")
    detected = has_public and (has_config or has_plugins)
    return detected, evidence

def detect_kotlin(base: Path) -> tuple[bool, list]:
    evidence = []
    kotlin_smali = find_files(base, "kotlin")
    for p in kotlin_smali:
        if p.is_dir():
            evidence.append(f"Found kotlin/ directory in smali: {p.relative_to(base)}")
            break
    kotlin_modules = find_files(base, "*.kotlin_module")
    if kotlin_modules:
        evidence.append(f"Found {len(kotlin_modules)} .kotlin_module file(s) in META-INF/")
    return len(evidence) > 0, evidence

def detect_java_or_native(base: Path) -> tuple[str, list]:
    evidence = []
    smali_files  = find_files(base, "*.smali")
    so_files     = find_files(base / "lib" if (base / "lib").is_dir() else base, "*.so")
    kotlin_smali = find_files(base, "kotlin")
    kotlin_dirs  = [p for p in kotlin_smali if p.is_dir()]

    has_smali  = len(smali_files) > 0
    has_so     = len(so_files) > 0
    has_kotlin = len(kotlin_dirs) > 0

    if has_smali and has_kotlin:
        evidence.append(f"Found {len(smali_files)} .smali file(s)")
        evidence.append("Found kotlin/ packages inside smali")
        return "Kotlin (likely)", evidence

    if has_smali:
        evidence.append(f"Found {len(smali_files)} .smali file(s)")
        evidence.append("No Kotlin or other framework indicators found")
        return "Java (likely)", evidence

    if has_so:
        evidence.append(f"Found {len(so_files)} .so file(s) with no smali present")
        return "Native C/C++ NDK (likely)", evidence

    return "Unknown / Undetected", evidence
DETECTORS = [
    ("Flutter",       detect_flutter),
    ("React Native",  detect_react_native),
    ("Unity",         detect_unity),
    ("Xamarin",       detect_xamarin),
    ("Ionic/Cordova", detect_cordova),
    ("Capacitor",     detect_capacitor),
    ("Kotlin",        detect_kotlin),
]
def detect_framework(decompiled_path: str) -> dict:
    base = Path(decompiled_path)
    results = []
    cprint("\n[*] Scanning decompiled files ...\n", Colors.CYAN)
    for name, detector in DETECTORS:
        detected, evidence = detector(base)
        results.append({
            "name":     name,
            "detected": detected,
            "evidence": evidence,
        })
    matched = [r for r in results if r["detected"]]
    if matched:
        return {
            "status":   "detected",
            "matches":  matched,
            "fallback": None,
        }
    fallback_name, fallback_evidence = detect_java_or_native(base)
    return {
        "status":   "fallback",
        "matches":  [],
        "fallback": {
            "name":     fallback_name,
            "evidence": fallback_evidence,
        },
    }
FRAMEWORK_ICONS = {
    "Flutter":                     "🟦",
    "React Native":                "⚛️ ",
    "Unity":                       "🎮",
    "Xamarin":                     "🔷",
    "Ionic/Cordova":               "🌐",
    "Capacitor":                   "🦕",
    "Kotlin":                      "🎯",
    "Java (likely)":               "☕",
    "Kotlin (likely)":             "🎯",
    "Native C/C++ NDK (likely)":   "⚙️ ",
    "Unknown / Undetected":        "❓",
}

def print_results(apk_path: str, result: dict):
    cprint("\n" + "=" * 55, Colors.BOLD)
    cprint(f"  Result for: {Path(apk_path).name}", Colors.BOLD)
    cprint("=" * 55, Colors.BOLD)
    if result["status"] == "detected":
        matches = result["matches"]
        if len(matches) == 1:
            fw   = matches[0]
            icon = FRAMEWORK_ICONS.get(fw["name"], "📦")
            cprint(f"\n  {icon}  Framework: {fw['name']}", Colors.GREEN + Colors.BOLD)
            cprint("\n  Evidence:", Colors.YELLOW)
            for ev in fw["evidence"]:
                cprint(f"    ✓ {ev}", Colors.YELLOW)
        else:
            cprint(
                f"\n  ⚠️  Multiple frameworks detected (hybrid app):",
                Colors.YELLOW + Colors.BOLD,
            )
            for fw in matches:
                icon = FRAMEWORK_ICONS.get(fw["name"], "📦")
                cprint(f"\n  {icon}  {fw['name']}", Colors.GREEN)
                for ev in fw["evidence"]:
                    cprint(f"    ✓ {ev}", Colors.YELLOW)

    else:
        fb   = result["fallback"]
        icon = FRAMEWORK_ICONS.get(fb["name"], "❓")
        if fb["name"] == "Unknown / Undetected":
            cprint(
                f"\n  {icon}  Framework could not be identified",
                Colors.RED + Colors.BOLD,
            )
            cprint(
                "  No recognizable signals found in the decompiled output.",
                Colors.RED,
            )
        else:
            cprint(f"\n  {icon}  Framework: {fb['name']}", Colors.CYAN + Colors.BOLD)
            cprint("  (Identified via fallback analysis)", Colors.CYAN)
            cprint("\n  Evidence:", Colors.YELLOW)
            for ev in fb["evidence"]:
                cprint(f"    ✓ {ev}", Colors.YELLOW)

    cprint("\n" + "=" * 55 + "\n", Colors.BOLD)
def main():
    parser = argparse.ArgumentParser(
        description="Detect the development framework of any Android APK file."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--apk",    help="Path to the APK file")
    source.add_argument("--folder", help="Path to an already-decompiled folder (skips apktool)")

    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep decompiled files after analysis (only relevant when using --apk)",
    )
    parser.add_argument(
        "--output-dir",
        help="Custom directory for apktool output (optional, only used with --apk)",
        default=None,
    )
    args = parser.parse_args()
    cprint(f"\n{'=' * 55}", Colors.BOLD)
    cprint("  APK Framework Detector", Colors.BOLD)
    cprint(f"{'=' * 55}", Colors.BOLD)
    if args.folder:
        folder_path = args.folder
        if not os.path.isdir(folder_path):
            cprint(f"[✗] Folder not found: {folder_path}", Colors.RED)
            sys.exit(1)

        cprint(f"  Mode       : folder (skipping apktool)", Colors.BLUE)
        cprint(f"  Folder     : {folder_path}", Colors.BLUE)

        result = detect_framework(folder_path)
        print_results(folder_path, result)
        return

    apk_path = args.apk

    if not os.path.isfile(apk_path):
        cprint(f"[✗] File not found: {apk_path}", Colors.RED)
        sys.exit(1)

    if not apk_path.lower().endswith(".apk"):
        cprint("[!] Warning: file does not have a .apk extension — proceeding anyway", Colors.YELLOW)

    use_temp = args.output_dir is None
    if use_temp:
        decompile_dir = tempfile.mkdtemp(prefix="apk_detector_")
    else:
        decompile_dir = args.output_dir
        os.makedirs(decompile_dir, exist_ok=True)

    cprint(f"  Mode       : apk", Colors.BLUE)
    cprint(f"  File       : {apk_path}", Colors.BLUE)
    cprint(f"  Output dir : {decompile_dir}", Colors.BLUE)

    try:
        success = run_apktool(apk_path, decompile_dir)
        if not success:
            cprint("[✗] Decompilation failed. Exiting.", Colors.RED)
            sys.exit(1)

        result = detect_framework(decompile_dir)
        print_results(apk_path, result)

    finally:
        if use_temp and not args.keep:
            cprint("[*] Cleaning up temporary files ...", Colors.CYAN)
            shutil.rmtree(decompile_dir, ignore_errors=True)
            cprint("[+] Cleanup done ✓", Colors.GREEN)
        else:
            cprint(f"[*] Decompiled files kept at: {decompile_dir}", Colors.CYAN)

if __name__ == "__main__":
    main()
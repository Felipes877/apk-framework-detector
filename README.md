# APK Framework Detector 🔍

A command-line tool that detects the development framework or language used to build any Android APK without needing to manually inspect its contents.

It works by decompiling the APK using **apktool** and analyzing the resulting files and folder structure to identify the underlying technology.

---

## Features

- Detects **8 major frameworks**: Flutter, React Native, Unity, Xamarin, Ionic/Cordova, Capacitor, Kotlin, and Java
- **Fallback analysis** for unrecognized apps - identifies Java (likely), Kotlin (likely), Native C/C++ NDK, or reports `Unknown / Undetected` honestly instead of guessing
- **Hybrid app detection** - if multiple frameworks are found, all of them are reported
- Displays **evidence** for every detection (exactly which files or folders triggered the result)
- Works directly on an **already-decompiled folder** - no need to run apktool manually every time
- **Cross-platform** - works on Windows, Linux, and macOS
- Automatically **cleans up** temporary decompiled files after analysis (can be disabled with `--keep`)
- No third-party Python libraries required - uses standard library only

---

## Requirements

### System
- **Python 3.10+**
- **apktool** installed and available on PATH
  - Windows: download `apktool.bat` from [https://apktool.org](https://apktool.org)
  - Linux: `sudo apt install apktool`
  - macOS: `brew install apktool`

### Python
No third-party packages required. All dependencies are part of the Python standard library.

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/smackerdodi/apk-framework-detector.git
cd apk-framework-detector
```

**2. Make sure apktool is working**
```bash
apktool --version        # Linux / macOS
apktool.bat --version    # Windows
```

---

## How to Run

### Mode 1 - Provide an APK file directly
The tool will decompile it automatically using apktool, analyze it, then clean up.

```bash
python3 apk_detector.py --apk path/to/app.apk
```

### Mode 2 - Provide an already-decompiled folder
If you already ran apktool manually, point the tool directly to the output folder.

```bash
python3 apk_detector.py --folder path/to/decompiled_folder
```

### Optional flags (APK mode only)

| Flag | Description |
|------|-------------|
| `--keep` | Keep the decompiled files after analysis instead of deleting them |
| `--output-dir <path>` | Use a specific folder for apktool output instead of a temp directory |

---

## Example Output

```
=======================================================
  APK Framework Detector
=======================================================
  Mode       : apk
  File       : instagram.apk
  Output dir : C:\Users\User\AppData\Local\Temp\apk_detector_xyz

[*] Running apktool.bat ...
[+] apktool finished successfully ✓

[*] Scanning decompiled files ...

=======================================================
  Result for: instagram.apk
=======================================================

  ⚛️   Framework: React Native

  Evidence:
    ✓ Found assets/index.android.bundle
    ✓ Found libreactnativejni.so in lib/

=======================================================

[*] Cleaning up temporary files ...
[+] Cleanup done ✓
```

---

## Supported Frameworks

| Icon | Framework | Detection Method |
|------|-----------|-----------------|
| 🟦 | Flutter | `libflutter.so`, `libapp.so`, `flutter_assets/` |
| ⚛️  | React Native | `index.android.bundle`, `libreactnativejni.so` |
| 🎮 | Unity | `libunity.so`, `libil2cpp.so`, `assets/bin/Data/` |
| 🔷 | Xamarin | `libmonodroid.so`, `assemblies/*.dll` |
| 🌐 | Ionic / Cordova | `assets/www/` + `cordova.js` or `cordova_plugins.js` |
| 🦕 | Capacitor | `assets/public/` + `capacitor.config.json` |
| 🎯 | Kotlin | `.kotlin_module` files, `kotlin/` smali packages |
| ☕ | Java | Fallback — smali files with no other framework signals |
| ⚙️  | Native C/C++ NDK | `.so` files present with no smali |
| ❓ | Unknown | No recognizable signals found |

---

## Notes

- **Timeout:** apktool is given up to **600 seconds (10 minutes)** to decompile. This is intentional to handle large APKs on slower machines.
- **Hybrid apps:** Some apps use more than one framework (e.g. a native app with an embedded React Native screen). The tool will report all detected frameworks.
- **Obfuscated APKs:** Heavily obfuscated apps may hide some signals, leading to a fallback or unknown result. This is expected behavior.

---

## License

MIT License - free to use, modify, and distribute.

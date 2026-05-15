# RifatCam Pro - Complete User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Desktop Application](#desktop-application)
4. [Android Application](#android-application)
5. [Advanced Features](#advanced-features)
6. [Network Configuration](#network-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Building from Source](#building-from-source)

---

## Introduction

RifatCam Pro transforms your Android phone into a wireless IP camera for your Windows PC. The system consists of two components:

- **Android App**: Captures camera video and streams it over HTTP (MJPEG)
- **Desktop Client**: Receives and displays the stream with a premium HUD interface

The communication happens entirely over your local Wi-Fi network - no internet required.

### How It Works

```
┌──────────────┐         Wi-Fi          ┌──────────────┐
│   Android    │ ◄─────── MJPEG ───────► │   Windows    │
│   Phone      │     Stream (HTTP)      │     PC       │
│  Port 8080   │                        │  PyQt6 App   │
└──────────────┘                        └──────────────┘
```

---

## Quick Start

### Step 1: Install Android App
1. Build and install the APK from Android Studio (see [Building from Source](#building-from-source))
2. Open RifatCam Pro on your phone
3. Grant camera permission

### Step 2: Launch Desktop Client
- Run `RifatCamPro.exe` (pre-built) or `python main.py` (from source)

### Step 3: Connect
1. On Android, tap **"START STREAM"**
2. On Desktop, click **"SCAN NETWORK"**
3. Select your device from the detected list
4. Video will appear automatically

---

## Desktop Application

### Interface Overview

The desktop interface is divided into several zones:

1. **Top Bar** - App title, connection status, FPS, resolution, device name
2. **Camera View** - Main video display with corner accents and scanline overlay
3. **Side Panel** - Device list, status information, network tools
4. **Control Bar** - All action buttons

### Controls Reference

#### Connection
| Action | Description |
|--------|-------------|
| CONNECT | Connect to last/auto-detected device |
| SCAN NETWORK | Search for RifatCam devices on local network |
| MANUAL CONNECT | Enter IP address of device manually |

#### Camera
| Action | Description |
|--------|-------------|
| 🔄 Switch Camera | Toggle between front and back camera |
| ⚡ Flash | Toggle camera flash (back camera only) |
| 🔍± Zoom | Adjust zoom level |
| ⊡ Reset Zoom | Return to 1x zoom |

#### Capture
| Action | Description |
|--------|-------------|
| 📷 Screenshot | Capture current frame as PNG |
| ● REC | Start/stop video recording |

#### Display
| Action | Description |
|--------|-------------|
| ⛶ Fullscreen | Toggle fullscreen mode |
| ⚙ Settings | Open settings dialog |

### Settings

#### Streaming Tab
- **Resolution**: 480p, 720p, or 1080p
- **FPS Limit**: 1-60 FPS
- **Auto-connect**: Automatically connect to last device

#### Recording Tab
- **Screenshot Auto-save**: Save screenshots automatically
- **Recording Format**: MP4 (H.264), MP4 (MPEG-4), or AVI (MJPEG)

#### Detection Tab
- **Motion Detection**: Enable/disable with sensitivity slider
- **AI Detection**: Face/human detection (requires YOLO model files)

---

## Android Application

### Interface

The Android app provides:

1. **Camera Preview** - Live view from phone camera
2. **Status Bar** - Connection status and stream URL
3. **Control Panel** - Stream control, camera settings, zoom

### Features

#### Streaming
- Tap **"START STREAM"** to begin broadcasting
- The stream URL is displayed on screen
- Other devices on the network can connect using this URL

#### Camera Controls
- **Switch Camera** - Toggle front/back
- **Flash** - Toggle flash (back only)
- **Resolution** - 480p / 720p / 1080p
- **Zoom** - Slider control (1x-5x)

#### QR Code
- Tap QR button to generate a QR code containing connection info
- Scan with desktop app for instant pairing

#### Background Service
- Streaming continues in the background
- Notification shows active streaming status
- Tap notification to return to app

---

## Advanced Features

### Motion Detection

The desktop client can detect motion in the video stream:

1. Open **Settings > Detection**
2. Enable **Motion Detection**
3. Adjust **Sensitivity** slider
4. Motion events are logged and can trigger actions

### AI Detection (Optional)

RifatCam Pro supports YOLO-based object detection:

1. Download YOLOv3 files:
   - `yolov3.cfg` - Model configuration
   - `yolov3.weights` - Model weights
   - `coco.names` - Class names

2. Place them in `%USERPROFILE%\.rifatcam\models\`

3. Enable AI detection in Settings

4. Detected objects will be highlighted on the video

### Keyboard Shortcuts (Desktop)

| Shortcut | Action |
|----------|--------|
| F11 | Toggle fullscreen |
| F12 | Take screenshot |
| Ctrl+R | Toggle recording |
| Ctrl+, | Open settings |
| Ctrl+D | Connect/disconnect |
| Escape | Exit fullscreen |

---

## Network Configuration

### Firewall

Ensure Windows Firewall allows:
- Inbound TCP port 8080 (or configure custom port)

```powershell
# Add firewall rule (run as Administrator)
netsh advfirewall firewall add rule name="RifatCam Pro" dir=in action=allow protocol=TCP localport=8080
```

### Custom Port

To change the streaming port:
1. Edit `NetworkUtils.kt` - change `STREAM_PORT` constant
2. Rebuild Android app
3. Desktop will use port from device info

### Static IP (Recommended)

For reliable connections, assign static IP to your Android device:
1. Go to **Wi-Fi Settings > Advanced > IP Settings**
2. Change from DHCP to **Static**
3. Set a fixed IP address

---

## Troubleshooting

### "No devices found"

| Cause | Solution |
|-------|----------|
| Different network | Ensure both devices on same Wi-Fi |
| Firewall blocking | Add firewall rule for port 8080 |
| Discovery port blocked | Try manual IP connection |
| Android not streaming | Tap "START STREAM" on phone |

### Stream not visible

| Cause | Solution |
|-------|----------|
| Wrong IP address | Verify IP on Android status bar |
| Port mismatch | Default port is 8080 |
| Camera in use | Close other camera apps |
| Network congestion | Lower resolution to 720p or 480p |

### Poor performance

| Cause | Solution |
|-------|----------|
| Wi-Fi interference | Move closer to router |
| High resolution | Switch to 720p or 480p |
| CPU overload | Close other applications |
| Background apps | Limit background processes |

### Recording issues

| Cause | Solution |
|-------|----------|
| Codec not available | Change recording format in settings |
| Disk space full | Free up disk space |
| Permission denied | Check write permissions to save folder |

---

## Building from Source

### Desktop Client (Windows)

```bash
# Prerequisites
# - Python 3.8 or higher
# - Git

# Clone/enter project
cd RifatCam-Pro/desktop-client

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py

# Build EXE
pyinstaller build.spec
# OR
pyinstaller --onefile --windowed --name "RifatCamPro" main.py
```

### Android App

```bash
# Prerequisites
# - Android Studio 2022.3+
# - Android SDK 34
# - JDK 17

cd RifatCam-Pro/android-app

# Build debug APK
./gradlew assembleDebug

# Build release APK (requires signing)
./gradlew assembleRelease

# Output located at:
# app/build/outputs/apk/debug/app-debug.apk
```

### Quick Build Script

```bash
cd installer
build_exe.bat
```

---

## File Locations

### Desktop
| Data | Path |
|------|------|
| Settings | `%USERPROFILE%\.rifatcam\settings.json` |
| Screenshots | `%USERPROFILE%\.rifatcam\screenshots\` |
| Recordings | `%USERPROFILE%\.rifatcam\recordings\` |
| AI Models | `%USERPROFILE%\.rifatcam\models\` |

### Android
| Data | Path |
|------|------|
| App Data | Internal storage `/data/data/com.rifatcam.pro/` |
| Logs | Logcat tag: `RifatCam-Main`, `StreamServer`, `CameraManager` |

---

## Support

For issues and feature requests:
- GitHub Issues: [https://github.com/rifatcam/rifatcam-pro/issues](https://github.com/rifatcam/rifatcam-pro/issues)
- Documentation: [https://rifatcam.com/docs](https://rifatcam.com/docs)

---

*Last updated: 2026-05-16*
*RifatCam Pro v1.0.0*

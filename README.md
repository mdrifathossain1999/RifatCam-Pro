# ◆ RifatCam Pro

**Premium Wi-Fi Camera Streaming Software**

Stream your **Android or iPhone** camera to your Windows PC over your local network in real-time. Features a premium Jarvis/Iron Man HUD interface with neon cyber aesthetic.

```
┌────────────────────────────────────────────┐
│  ◆ RIFATCAM PRO          FPS: 30 │ 720p   │
│────────────────────────────────────────────│
│                                            │
│           ● LIVE CAMERA VIEW               │
│                                            │
│────────────────────────────────────────────│
│  [CONNECT] [📷] [● REC] [⛶] [⚙]        │
└────────────────────────────────────────────┘
```

## Features

### 📡 Live Streaming
- Real-time MJPEG video streaming over Wi-Fi
- 480p / 720p / 1080p resolution support
- Low-latency streaming protocol
- Auto-reconnect on connection loss

### 🔗 Connection
- **Auto Discovery** - Desktop automatically finds your phone on the network
- **QR Code Pairing** - Scan QR code from phone to connect instantly
- **Manual Connect** - Enter IP address manually
- **USB Fallback** - Architecture ready for USB tethering

### 🎨 Premium UI (Desktop)
- Futuristic Jarvis/Iron Man HUD interface
- Dark theme with blue neon glow effects
- Glassmorphism design language
- Animated controls and smooth transitions
- Corner accent overlays and scanline effects
- Real-time FPS counter and status indicators

### 📷 Camera Controls
- Front/Back camera switching
- Pinch-to-zoom and slider zoom
- Flash toggle (back camera only)
- Resolution selection
- Auto-focus support

### 🎥 Recording & Capture
- One-click video recording (MP4/H.264)
- Screenshot capture (PNG)
- Auto-save to organized folders
- Recording timer

### 🔍 Detection (Optional)
- Motion detection with configurable sensitivity
- AI detection architecture (YOLO/OpenCV DNN)
- Face detection via Haar Cascade
- Real-time detection overlays

## Project Structure

```
RifatCam-Pro/
│
├── desktop-client/          # Windows desktop application
│   ├── main.py              # Entry point
│   ├── requirements.txt     # Python dependencies
│   ├── build.spec           # PyInstaller build spec
│   ├── ui/                  # User interface components
│   │   ├── main_window.py   # Main application window
│   │   ├── camera_widget.py # Video display widget
│   │   ├── hud_overlay.py   # HUD overlay elements
│   │   ├── settings_dialog.py # Settings panel
│   │   └── styles.py        # QSS stylesheets & theme
│   ├── core/                # Core functionality
│   │   ├── stream_receiver.py  # MJPEG stream client
│   │   ├── recorder.py      # Video recording & screenshots
│   │   ├── motion_detector.py # Motion detection
│   │   ├── network_scanner.py # Network device discovery
│   │   └── detector.py      # AI/cv2 object detection
│   ├── utils/               # Utilities & helpers
│   │   └── helpers.py       # Config, paths, network utils
│   └── assets/              # Icons and resources
│
├── android-app/             # Android streaming app
├── ios-app/                 # iOS streaming app
│   ├── build.gradle.kts     # Root build config
│   ├── settings.gradle.kts  # Gradle settings
│   ├── gradle.properties    # Build properties
│   └── app/
│       ├── build.gradle.kts # App build config
│       └── src/main/
│           ├── AndroidManifest.xml
│           ├── res/         # Resources (layouts, drawables)
│           └── java/com/rifatcam/pro/
│               ├── MainActivity.kt       # Main UI & controller
│               ├── CameraStreamService.kt # Background service
│               ├── StreamServer.kt        # HTTP MJPEG server
│               ├── CameraManager.kt       # CameraX manager
│               ├── QRCodeHelper.kt        # QR code generation
│               └── NetworkUtils.kt        # Network utilities
│
├── installer/               # Build & packaging
│   └── build_exe.bat        # Windows EXE builder
│
├── docs/                    # Documentation
│   └── guide.md             # Full user guide
│
└── README.md                # This file
```

## Installation

### Desktop Client (Windows)

#### Method 1: Pre-built EXE
1. Download `RifatCamPro.exe` from the releases page
2. Run the executable - no installation required

#### Method 2: From Source
```bash
# Clone or navigate to the project
cd RifatCam-Pro/desktop-client

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Or build EXE
pyinstaller build.spec
# Output: dist/RifatCamPro.exe
```

### iOS App (iPhone)

#### Prerequisites
- macOS with Xcode 15+
- iOS 15.0+ device
- Apple Developer account (free is fine)

#### Build with XcodeGen (Recommended)
```bash
cd RifatCam-Pro/ios-app
brew install xcodegen   # if not installed
xcodegen
open RifatCamPro.xcodeproj
# Select your iPhone → Run (⌘R)
```

#### Manual Setup
1. Open Xcode → New Project → iOS → App (Swift, UIKit)
2. Replace/create files with those in `ios-app/RifatCamPro/`
3. Set deployment target to iOS 15.0
4. Run on your iPhone

### Android App

#### Build with Android Studio
1. Open `RifatCam-Pro/android-app/` in Android Studio
2. Wait for Gradle sync to complete
3. Connect your Android device (USB debugging enabled)
4. Click **Run** (▶) to install on your device

#### Build APK
```bash
cd RifatCam-Pro/android-app
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/app-release.apk
```

## Usage Guide

### 1. Setup Network
- Connect both devices to the **same Wi-Fi network**
- Ensure no firewall blocks port 8080

### 2. Start Android App
- Open RifatCam Pro on your phone
- Grant camera permission when prompted
- Tap **"START STREAM"**
- Note the IP address shown on screen

### 3. Connect from Desktop
- Launch RifatCam Pro on your PC
- Click **"SCAN NETWORK"** to discover your phone
- Or enter the IP address manually
- Click **"CONNECT"** to start viewing

### 4. Controls
| Button | Action |
|--------|--------|
| CONNECT | Connect/disconnect to device |
| 📷 | Take screenshot |
| ● REC | Start/stop video recording |
| 🔄 | Switch front/back camera |
| ⚡ | Toggle flash |
| 🔍+ | Zoom in |
| 🔍− | Zoom out |
| ⛶ | Toggle fullscreen |
| ⚙ | Open settings |

## Requirements

### Desktop
- **OS:** Windows 10/11 (64-bit)
- **Python:** 3.8 or higher
- **RAM:** 4 GB minimum (8 GB recommended)
- **Network:** Wi-Fi adapter

### Android
- **OS:** Android 8.0 (API 26) or higher
- **Camera:** Any built-in camera
- **Network:** Wi-Fi connection

## Tech Stack

### Desktop
| Component | Technology |
|-----------|------------|
| UI Framework | PyQt6 |
| Video Processing | OpenCV, NumPy, Pillow |
| Networking | Socket, Requests |
| Stream Protocol | MJPEG over HTTP |
| Packaging | PyInstaller |

### Android
| Component | Technology |
|-----------|------------|
| Language | Kotlin |
| Camera API | CameraX |
| Streaming | HTTP MJPEG Server |
| QR Code | ZXing |
| Build | Gradle KTS |

### iOS
| Component | Technology |
|-----------|------------|
| Language | Swift 5.9 |
| Camera API | AVFoundation |
| Streaming | HTTP MJPEG Server |
| QR Code | CoreImage (CIQRCodeGenerator) |
| Build | Xcode 15+ |

## Troubleshooting

### Connection Issues
- Ensure both devices are on the same Wi-Fi network
- Check Windows Firewall (allow port 8080)
- Try manual IP connection if auto-discovery fails
- Restart both applications

### Stream Lag
- Use 720p instead of 1080p
- Ensure strong Wi-Fi signal
- Close other bandwidth-intensive applications
- Reduce FPS limit in settings

### Camera Not Working
- Check camera permissions on Android
- Restart the Android app
- Try switching between front/back camera
- Ensure no other app is using the camera

### App Crashes
- Update graphics drivers
- Ensure Python 3.8+ is installed
- Reinstall dependencies with `pip install -r requirements.txt`

## License

© 2026 RifatCam. All rights reserved.

---

**Built with ❤ by the RifatCam team**

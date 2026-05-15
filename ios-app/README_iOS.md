# RifatCam Pro - iOS App

## Prerequisites

- **macOS** Ventura 13+ or Sonoma 14+
- **Xcode** 15.0 or later
- **iOS** 15.0+ device (iPhone or iPad)
- Apple Developer account (free or paid)

## Quick Start (XcodeGen)

The easiest way to build:

```bash
# Install XcodeGen (if not installed)
brew install xcodegen

# Generate Xcode project
cd RifatCam-Pro/ios-app
xcodegen

# Open project
open RifatCamPro.xcodeproj
```

Then: Select your device → **Run (⌘R)**

## Manual Xcode Setup

If you don't have XcodeGen:

1. Open **Xcode** → **Create New Project** → **iOS → App**
2. Choose: Swift, UIKit App Delegate, **not** SwiftUI
3. Save in the `ios-app/` folder
4. Replace/create files with the provided Swift files:

| File | Action |
|------|--------|
| `RifatCamPro/AppDelegate.swift` | Replace |
| `RifatCamPro/SceneDelegate.swift` | Replace |
| `RifatCamPro/ViewController.swift` | Replace |
| `RifatCamPro/CameraManager.swift` | Add new |
| `RifatCamPro/StreamServer.swift` | Add new |
| `RifatCamPro/NetworkUtils.swift` | Add new |
| `RifatCamPro/QRCodeHelper.swift` | Add new |
| `RifatCamPro/Info.plist` | Replace |

5. Set **Deployment Target** to **iOS 15.0**
6. Connect your iPhone and run

## Permissions

The app requires:
- **Camera** (NSCameraUsageDescription) - already in Info.plist
- **Local Network** (NSLocalNetworkUsageDescription) - already in Info.plist

These will prompt on first launch.

## Build & Install

### Debug (for testing)
```bash
# In Xcode: Select your iPhone → Run (⌘R)
```

### Release (for personal use)
```bash
# Xcode → Product → Archive
# Then: Distribute App → Development
```

## Architecture

```
┌──────────────────────────────────────────────┐
│           ViewController (UI)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ Camera   │ │ Stream   │ │ QRCodeHelper │ │
│  │ Manager  │ │ Server   │ │              │ │
│  │          │ │          │ │ QR generation│ │
│  │ AVFound- │ │ HTTP     │ │ + parsing    │ │
│  │ ation    │ │ MJPEG    │ └──────────────┘ │
│  └──────────┘ └──────────┘                  │
│  ┌──────────────────────────────────────────┐│
│  │         NetworkUtils                     ││
│  │  (IP detection, discovery protocol)      ││
│  └──────────────────────────────────────────┘│
└──────────────────────────────────────────────┘
```

## iOS vs Android Limitations

| Feature | iOS | Android |
|---------|-----|---------|
| Background stream | ❌ Limited | ✅ Full |
| Camera access | ✅ | ✅ |
| Flashlight | ✅ (back only) | ✅ |
| Front camera | ✅ | ✅ |
| Resolution change | ✅ | ✅ |
| QR code | ✅ (built-in) | ✅ (ZXing) |
| Auto-discovery | ✅ | ✅ |

On iOS, camera access is only available while the app is in the foreground.
The stream will pause if the app goes to background.

## Streaming Protocol

Same as Android version:
- HTTP server on port **8080**
- MJPEG endpoint: `/video`
- Device info: `/info`
- Control: `/control`
- Web UI: `/`

## Usage

1. **Connect to Wi-Fi** (both iPhone and PC on same network)
2. **Open RifatCam Pro** on iPhone
3. Grant camera permission
4. Tap **"● START"**
5. On desktop RifatCam Pro: scan network or enter the IP shown
6. Stream will appear on desktop!

## Troubleshooting

### Xcode build errors
- Ensure deployment target is iOS 15.0+
- Make sure Info.plist has all required keys
- Clean build folder (⌘⇧K) and rebuild

### Camera not working
- Check camera permission in Settings → Privacy → Camera
- Restart the app
- Try switching front/back camera

### No stream on desktop
- Both devices must be on the **same Wi-Fi network**
- Check firewall isn't blocking port 8080
- Desktop: try manual IP connection if auto-discovery fails

import UIKit
import AVFoundation
import CoreVideo

protocol CameraManagerDelegate: AnyObject {
    func cameraManagerDidCaptureFrame(jpegData: Data)
    func cameraManagerDidEncounterError(_ error: Error)
}

class CameraManager: NSObject {
    weak var delegate: CameraManagerDelegate?

    let captureSession = AVCaptureSession()
    private let videoOutput = AVCaptureVideoDataOutput()
    private var backCamera: AVCaptureDevice?
    private var frontCamera: AVCaptureDevice?
    private var currentInput: AVCaptureDeviceInput?
    private let sessionQueue = DispatchQueue(label: "camera.session.queue", qos: .userInitiated)
    private let processingQueue = DispatchQueue(label: "camera.processing.queue", qos: .default)
    private let ciContext = CIContext()

    private let isStreamingLock = NSLock()
    private var _isStreaming = false
    private var isStreaming: Bool {
        get {
            isStreamingLock.lock()
            let val = _isStreaming
            isStreamingLock.unlock()
            return val
        }
        set {
            isStreamingLock.lock()
            _isStreaming = newValue
            isStreamingLock.unlock()
        }
    }

    private let cameraStateLock = NSLock()
    private(set) var usingBackCamera = true

    var onReady: (() -> Void)?

    override init() {
        super.init()
    }

    func requestPermission(completion: @escaping (Bool) -> Void) {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            completion(true)
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async { completion(granted) }
            }
        default:
            completion(false)
        }
    }

    func setupCamera() {
        sessionQueue.async { [weak self] in
            guard let self = self else { return }
            self.captureSession.beginConfiguration()
            self.captureSession.sessionPreset = .high

            let discoverySession = AVCaptureDevice.DiscoverySession(
                deviceTypes: [.builtInWideAngleCamera],
                mediaType: .video,
                position: .unspecified
            )

            for device in discoverySession.devices {
                if device.position == .back { self.backCamera = device }
                if device.position == .front { self.frontCamera = device }
            }

            guard let initialDevice = self.backCamera ?? self.frontCamera else {
                print("[Camera] No camera found")
                self.captureSession.commitConfiguration()
                return
            }

            do {
                let input = try AVCaptureDeviceInput(device: initialDevice)
                if self.captureSession.canAddInput(input) {
                    self.captureSession.addInput(input)
                    self.cameraStateLock.lock()
                    self.currentInput = input
                    self.cameraStateLock.unlock()
                }
            } catch {
                print("[Camera] Input error: \(error)")
                self.captureSession.commitConfiguration()
                return
            }

            self.videoOutput.setSampleBufferDelegate(self, queue: self.processingQueue)
            self.videoOutput.alwaysDiscardsLateVideoFrames = true
            self.videoOutput.videoSettings = [
                kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA
            ]

            if self.captureSession.canAddOutput(self.videoOutput) {
                self.captureSession.addOutput(self.videoOutput)
            }

            self.captureSession.commitConfiguration()
            print("[Camera] Setup complete")
        }
    }

    func startSession() {
        sessionQueue.async { [weak self] in
            guard let self = self, !self.captureSession.isRunning else { return }
            self.captureSession.startRunning()
            print("[Camera] Session started")
            DispatchQueue.main.async {
                self.onReady?()
            }
        }
    }

    func stopSession() {
        sessionQueue.async { [weak self] in
            guard let self = self, self.captureSession.isRunning else { return }
            self.captureSession.stopRunning()
            print("[Camera] Session stopped")
            self.isStreaming = false
        }
    }

    func switchCamera() {
        sessionQueue.async { [weak self] in
            guard let self = self else { return }

            self.cameraStateLock.lock()
            let currentUsingBack = self.usingBackCamera
            let newDevice: AVCaptureDevice? = currentUsingBack ? self.frontCamera : self.backCamera
            guard let device = newDevice else {
                self.cameraStateLock.unlock()
                return
            }

            self.captureSession.beginConfiguration()
            if let input = self.currentInput {
                self.captureSession.removeInput(input)
            }
            do {
                let newInput = try AVCaptureDeviceInput(device: device)
                if self.captureSession.canAddInput(newInput) {
                    self.captureSession.addInput(newInput)
                    self.currentInput = newInput
                    self.usingBackCamera = !currentUsingBack
                }
            } catch {
                if let input = self.currentInput {
                    self.captureSession.addInput(input)
                }
            }
            self.cameraStateLock.unlock()
            self.captureSession.commitConfiguration()
            print("[Camera] Switched to \(self.usingBackCamera ? "back" : "front") camera")
        }
    }

    func setResolution(width: Int32, height: Int32) {
        let preset: AVCaptureSession.Preset
        switch (width, height) {
        case (1920, 1080): preset = .hd1920x1080
        case (1280, 720):  preset = .hd1280x720
        case (640, 480):   preset = .vga640x480
        default:           preset = .high
        }
        sessionQueue.async { [weak self] in
            guard let self = self, self.captureSession.canSetSessionPreset(preset) else { return }
            self.captureSession.sessionPreset = preset
            print("[Camera] Resolution set to \(width)x\(height)")
        }
    }

    func toggleFlash() -> Bool {
        cameraStateLock.lock()
        let device = usingBackCamera ? backCamera : nil
        cameraStateLock.unlock()
        guard let device = device, device.hasTorch else { return false }
        do {
            try device.lockForConfiguration()
            device.torchMode = device.torchMode == .on ? .off : .on
            device.unlockForConfiguration()
            return device.torchMode == .on
        } catch {
            return false
        }
    }

    func setZoom(_ factor: CGFloat) {
        cameraStateLock.lock()
        let device = currentInput?.device
        cameraStateLock.unlock()
        guard let device = device else { return }
        do {
            try device.lockForConfiguration()
            device.videoZoomFactor = max(1.0, min(factor, device.activeFormat.videoMaxZoomFactor))
            device.unlockForConfiguration()
        } catch {}
    }

    func startStreaming() {
        isStreaming = true
    }

    func stopStreaming() {
        isStreaming = false
    }
}

extension CameraManager: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard isStreaming else { return }
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }

        let ciImage = CIImage(cvPixelBuffer: imageBuffer)

        guard let cgImage = ciContext.createCGImage(ciImage, from: ciImage.extent) else { return }

        let data = NSMutableData()
        guard let destination = CGImageDestinationCreateWithData(data as CFMutableData, "public.jpeg" as CFString, 1, nil) else { return }
        let properties: CFDictionary = [kCGImageDestinationLossyCompressionQuality: 0.85] as CFDictionary
        CGImageDestinationAddImage(destination, cgImage, properties)
        CGImageDestinationFinalize(destination)

        delegate?.cameraManagerDidCaptureFrame(jpegData: data as Data)
    }
}

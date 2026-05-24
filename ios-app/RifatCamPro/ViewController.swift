import UIKit
import AVFoundation

class ViewController: UIViewController, CameraManagerDelegate {
    // Loading indicator shown while camera is being prepared
    private let loadingLabel: UILabel = {
        let label = UILabel()
        label.text = "Loading..."
        label.textColor = .white
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    // MARK: - Properties
    private let cameraManager = CameraManager()
    private let streamServer = StreamServer()
    private var isStreaming = false

    // MARK: - UI Elements
    private let previewView = UIView()
    private let topBar = UIView()
    private let titleLabel = UILabel()
    private let clientLabel = UILabel()

    private let previewContainer = UIView()
    private let statusLabel = UILabel()
    private let urlLabel = UILabel()

    private let controlPanel = UIView()
    private let startStopBtn = UIButton(type: .system)
    private let switchCamBtn = UIButton(type: .system)
    private let flashBtn = UIButton(type: .system)
    private let qrBtn = UIButton(type: .system)

    private let bottomPanel = UIView()
    private let resolutionControl = UISegmentedControl(items: ["480p", "720p", "1080p"])
    private let zoomSlider = UISlider()

    private let qrImageView = UIImageView()

    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 10/255, green: 14/255, blue: 23/255, alpha: 1)
        setupUI()
        setupCamera()
    }

    override var prefersStatusBarHidden: Bool { return false }
    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    // MARK: - Camera Setup
    private func setupCamera() {
        cameraManager.requestPermission { [weak self] granted in
            guard let self = self else { return }
            guard granted else {
                let alert = UIAlertController(title: "Camera Required", message: "Camera permission is needed for streaming.", preferredStyle: .alert)
                alert.addAction(UIAlertAction(title: "OK", style: .default))
                self.present(alert, animated: true)
                return
            }
            self.cameraManager.delegate = self
            self.cameraManager.onReady = { [weak self] in
                self?.addPreviewLayer()
            }
            self.cameraManager.setupCamera()
            self.cameraManager.startSession()
        }
    }

    private func addPreviewLayer() {
        // Hide loading indicator once preview is ready
        let layer = AVCaptureVideoPreviewLayer(session: cameraManager.captureSession)
        layer.frame = previewContainer.bounds
        layer.videoGravity = .resizeAspectFill
        layer.cornerRadius = 12
        layer.masksToBounds = true
        previewContainer.layer.insertSublayer(layer, at: 0)
        previewContainer.layer.borderWidth = 1
        previewContainer.layer.borderColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 0.15).cgColor
        previewContainer.layer.cornerRadius = 12
        loadingLabel.isHidden = true
    }

    // MARK: - CameraManagerDelegate
    func cameraManagerDidCaptureFrame(jpegData: Data) {
        streamServer.updateJPEG(jpegData)
    }

    func cameraManagerDidEncounterError(_ error: Error) {
        print("[Camera] Error: \(error.localizedDescription)")
    }

    // MARK: - Actions
    @objc private func toggleStream() {
        if isStreaming {
            stopStream()
        } else {
            startStream()
        }
    }

    private func startStream() {
        guard NetworkUtils.isWifiConnected() else {
            showAlert(title: "Wi-Fi Required", message: "Please connect to Wi-Fi to start streaming.")
            return
        }

        let resIndex = resolutionControl.selectedSegmentIndex
        switch resIndex {
        case 0: cameraManager.setResolution(width: 640, height: 480)
        case 1: cameraManager.setResolution(width: 1280, height: 720)
        case 2: cameraManager.setResolution(width: 1920, height: 1080)
        default: cameraManager.setResolution(width: 1280, height: 720)
        }

        cameraManager.startStreaming()
        streamServer.start()

        isStreaming = true
        updateUIForStreaming()

        let ip = NetworkUtils.getWiFiAddress() ?? "unknown"
        urlLabel.text = "http://\(ip):\(NetworkUtils.streamPort)"
        statusLabel.text = "● STREAMING LIVE"
        statusLabel.textColor = UIColor(red: 1, green: 51/255, blue: 102/255, alpha: 1)

        UIApplication.shared.isIdleTimerDisabled = true
    }

    private func stopStream() {
        cameraManager.stopStreaming()
        streamServer.stop()

        isStreaming = false
        updateUIForStopped()

        statusLabel.text = "● Ready"
        statusLabel.textColor = UIColor(red: 0, green: 1, blue: 136/255, alpha: 1)
        urlLabel.text = "Not streaming"

        UIApplication.shared.isIdleTimerDisabled = false
    }

    @objc private func switchCamera() {
        cameraManager.switchCamera()
    }

    @objc private func toggleFlash() {
        let enabled = cameraManager.toggleFlash()
        flashBtn.alpha = enabled ? 1.0 : 0.4
    }

    @objc private func showQRCode() {
        let content = QRCodeHelper.generateStreamQRContent()
        guard !content.isEmpty, let image = QRCodeHelper.generateQRCode(from: content) else { return }

        qrImageView.image = image
        qrImageView.isHidden = false
        qrImageView.alpha = 0

        let ip = NetworkUtils.getWiFiAddress() ?? "unknown"
        urlLabel.text = "http://\(ip):\(NetworkUtils.streamPort)"

        UIView.animate(withDuration: 0.3) {
            self.qrImageView.alpha = 1
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 10) { [weak self] in
            UIView.animate(withDuration: 0.3) {
                self?.qrImageView.isHidden = true
            }
        }
    }

    @objc private func resolutionChanged(_ sender: UISegmentedControl) {
        switch sender.selectedSegmentIndex {
        case 0: cameraManager.setResolution(width: 640, height: 480)
        case 1: cameraManager.setResolution(width: 1280, height: 720)
        case 2: cameraManager.setResolution(width: 1920, height: 1080)
        default: break
        }
    }

    @objc private func zoomChanged(_ sender: UISlider) {
        let factor = 1.0 + CGFloat(sender.value) * 4.0
        cameraManager.setZoom(factor)
    }

    // MARK: - UI Updates
    private func updateUIForStreaming() {
        startStopBtn.setTitle("■ STOP", for: .normal)
        startStopBtn.backgroundColor = UIColor(red: 1, green: 51/255, blue: 102/255, alpha: 0.2)
        startStopBtn.layer.borderColor = UIColor(red: 1, green: 51/255, blue: 102/255, alpha: 0.8).cgColor
        startStopBtn.setTitleColor(UIColor(red: 1, green: 51/255, blue: 102/255, alpha: 1), for: .normal)
    }

    private func updateUIForStopped() {
        startStopBtn.setTitle("● START", for: .normal)
        startStopBtn.backgroundColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 0.12)
        startStopBtn.layer.borderColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 0.4).cgColor
        startStopBtn.setTitleColor(UIColor(red: 0, green: 212/255, blue: 1, alpha: 1), for: .normal)
        clientLabel.text = "Clients: 0"
    }

    // MARK: - UI Setup
    private func setupUI() {
        // Add loading label
        view.addSubview(loadingLabel)
        NSLayoutConstraint.activate([
            loadingLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
        setupTopBar()
        setupPreview()
        setupControls()
        setupBottomPanel()
        setupQRImageView()
        setupConstraints()
    }

    private func setupTopBar() {
        topBar.backgroundColor = UIColor(red: 17/255, green: 24/255, blue: 34/255, alpha: 1)
        topBar.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(topBar)

        titleLabel.text = "◆ RIFATCAM PRO"
        titleLabel.textColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 1)
        titleLabel.font = UIFont.systemFont(ofSize: 16, weight: .bold)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        topBar.addSubview(titleLabel)

        clientLabel.text = "Clients: 0"
        clientLabel.textColor = UIColor(red: 136/255, green: 153/255, blue: 170/255, alpha: 1)
        clientLabel.font = UIFont.systemFont(ofSize: 12)
        clientLabel.translatesAutoresizingMaskIntoConstraints = false
        topBar.addSubview(clientLabel)
    }

    private func setupPreview() {
        previewContainer.backgroundColor = UIColor(red: 10/255, green: 14/255, blue: 23/255, alpha: 1)
        previewContainer.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(previewContainer)

        statusLabel.text = "● Ready"
        statusLabel.textColor = UIColor(red: 0, green: 1, blue: 136/255, alpha: 1)
        statusLabel.font = UIFont.systemFont(ofSize: 12, weight: .medium)
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        previewContainer.addSubview(statusLabel)

        urlLabel.text = "Not streaming"
        urlLabel.textColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 1)
        urlLabel.font = UIFont.monospacedSystemFont(ofSize: 11, weight: .regular)
        urlLabel.translatesAutoresizingMaskIntoConstraints = false
        previewContainer.addSubview(urlLabel)
    }

    private func setupControls() {
        controlPanel.backgroundColor = UIColor(red: 17/255, green: 24/255, blue: 34/255, alpha: 1)
        controlPanel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(controlPanel)

        startStopBtn.setTitle("● START", for: .normal)
        startStopBtn.backgroundColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 0.12)
        startStopBtn.layer.borderColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 0.4).cgColor
        startStopBtn.layer.borderWidth = 1
        startStopBtn.layer.cornerRadius = 10
        startStopBtn.setTitleColor(UIColor(red: 0, green: 212/255, blue: 1, alpha: 1), for: .normal)
        startStopBtn.titleLabel?.font = UIFont.systemFont(ofSize: 15, weight: .bold)
        startStopBtn.addTarget(self, action: #selector(toggleStream), for: .touchUpInside)
        startStopBtn.translatesAutoresizingMaskIntoConstraints = false
        controlPanel.addSubview(startStopBtn)

        switchCamBtn.setImage(UIImage(systemName: "arrow.triangle.2.circlepath.camera"), for: .normal)
        switchCamBtn.tintColor = UIColor(red: 136/255, green: 153/255, blue: 170/255, alpha: 1)
        switchCamBtn.backgroundColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.04)
        switchCamBtn.layer.cornerRadius = 10
        switchCamBtn.layer.borderWidth = 0.5
        switchCamBtn.layer.borderColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.1).cgColor
        switchCamBtn.addTarget(self, action: #selector(switchCamera), for: .touchUpInside)
        switchCamBtn.translatesAutoresizingMaskIntoConstraints = false
        controlPanel.addSubview(switchCamBtn)

        flashBtn.setImage(UIImage(systemName: "bolt"), for: .normal)
        flashBtn.tintColor = UIColor(red: 136/255, green: 153/255, blue: 170/255, alpha: 1)
        flashBtn.alpha = 0.4
        flashBtn.backgroundColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.04)
        flashBtn.layer.cornerRadius = 10
        flashBtn.layer.borderWidth = 0.5
        flashBtn.layer.borderColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.1).cgColor
        flashBtn.addTarget(self, action: #selector(toggleFlash), for: .touchUpInside)
        flashBtn.translatesAutoresizingMaskIntoConstraints = false
        controlPanel.addSubview(flashBtn)

        qrBtn.setImage(UIImage(systemName: "qrcode"), for: .normal)
        qrBtn.tintColor = UIColor(red: 136/255, green: 153/255, blue: 170/255, alpha: 1)
        qrBtn.backgroundColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.04)
        qrBtn.layer.cornerRadius = 10
        qrBtn.layer.borderWidth = 0.5
        qrBtn.layer.borderColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.1).cgColor
        qrBtn.addTarget(self, action: #selector(showQRCode), for: .touchUpInside)
        qrBtn.translatesAutoresizingMaskIntoConstraints = false
        controlPanel.addSubview(qrBtn)
    }

    private func setupBottomPanel() {
        bottomPanel.backgroundColor = UIColor(red: 17/255, green: 24/255, blue: 34/255, alpha: 1)
        bottomPanel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(bottomPanel)

        resolutionControl.selectedSegmentIndex = 1
        resolutionControl.addTarget(self, action: #selector(resolutionChanged), for: .valueChanged)
        resolutionControl.translatesAutoresizingMaskIntoConstraints = false
        bottomPanel.addSubview(resolutionControl)

        zoomSlider.minimumValue = 0
        zoomSlider.maximumValue = 100
        zoomSlider.value = 0
        zoomSlider.tintColor = UIColor(red: 0, green: 212/255, blue: 1, alpha: 1)
        zoomSlider.addTarget(self, action: #selector(zoomChanged), for: .valueChanged)
        zoomSlider.translatesAutoresizingMaskIntoConstraints = false
        bottomPanel.addSubview(zoomSlider)
    }

    private func setupQRImageView() {
        qrImageView.contentMode = .scaleAspectFit
        qrImageView.backgroundColor = UIColor(red: 1, green: 1, blue: 1, alpha: 0.95)
        qrImageView.layer.cornerRadius = 12
        qrImageView.layer.masksToBounds = true
        qrImageView.isHidden = true
        qrImageView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(qrImageView)
    }

    private func setupConstraints() {
        NSLayoutConstraint.activate([
            topBar.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            topBar.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            topBar.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            topBar.heightAnchor.constraint(equalToConstant: 50),

            titleLabel.centerYAnchor.constraint(equalTo: topBar.centerYAnchor),
            titleLabel.leadingAnchor.constraint(equalTo: topBar.leadingAnchor, constant: 16),

            clientLabel.centerYAnchor.constraint(equalTo: topBar.centerYAnchor),
            clientLabel.trailingAnchor.constraint(equalTo: topBar.trailingAnchor, constant: -16),

            previewContainer.topAnchor.constraint(equalTo: topBar.bottomAnchor, constant: 8),
            previewContainer.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            previewContainer.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -8),

            statusLabel.topAnchor.constraint(equalTo: previewContainer.topAnchor, constant: 12),
            statusLabel.leadingAnchor.constraint(equalTo: previewContainer.leadingAnchor, constant: 12),

            urlLabel.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 4),
            urlLabel.leadingAnchor.constraint(equalTo: previewContainer.leadingAnchor, constant: 12),

            controlPanel.topAnchor.constraint(equalTo: previewContainer.bottomAnchor, constant: 8),
            controlPanel.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            controlPanel.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            controlPanel.heightAnchor.constraint(equalToConstant: 64),

            startStopBtn.centerYAnchor.constraint(equalTo: controlPanel.centerYAnchor),
            startStopBtn.leadingAnchor.constraint(equalTo: controlPanel.leadingAnchor, constant: 12),
            startStopBtn.widthAnchor.constraint(equalTo: controlPanel.widthAnchor, multiplier: 0.35),
            startStopBtn.heightAnchor.constraint(equalToConstant: 44),

            switchCamBtn.centerYAnchor.constraint(equalTo: controlPanel.centerYAnchor),
            switchCamBtn.leadingAnchor.constraint(equalTo: startStopBtn.trailingAnchor, constant: 8),
            switchCamBtn.widthAnchor.constraint(equalToConstant: 44),
            switchCamBtn.heightAnchor.constraint(equalToConstant: 44),

            flashBtn.centerYAnchor.constraint(equalTo: controlPanel.centerYAnchor),
            flashBtn.leadingAnchor.constraint(equalTo: switchCamBtn.trailingAnchor, constant: 8),
            flashBtn.widthAnchor.constraint(equalToConstant: 44),
            flashBtn.heightAnchor.constraint(equalToConstant: 44),

            qrBtn.centerYAnchor.constraint(equalTo: controlPanel.centerYAnchor),
            qrBtn.leadingAnchor.constraint(equalTo: flashBtn.trailingAnchor, constant: 8),
            qrBtn.widthAnchor.constraint(equalToConstant: 44),
            qrBtn.heightAnchor.constraint(equalToConstant: 44),

            bottomPanel.topAnchor.constraint(equalTo: controlPanel.bottomAnchor),
            bottomPanel.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            bottomPanel.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            bottomPanel.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),

            resolutionControl.topAnchor.constraint(equalTo: bottomPanel.topAnchor, constant: 8),
            resolutionControl.centerXAnchor.constraint(equalTo: bottomPanel.centerXAnchor),
            resolutionControl.widthAnchor.constraint(equalTo: bottomPanel.widthAnchor, multiplier: 0.6),

            zoomSlider.topAnchor.constraint(equalTo: resolutionControl.bottomAnchor, constant: 8),
            zoomSlider.leadingAnchor.constraint(equalTo: bottomPanel.leadingAnchor, constant: 16),
            zoomSlider.trailingAnchor.constraint(equalTo: bottomPanel.trailingAnchor, constant: -16),
            zoomSlider.bottomAnchor.constraint(equalTo: bottomPanel.bottomAnchor, constant: -8),

            qrImageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            qrImageView.centerYAnchor.constraint(equalTo: previewContainer.centerYAnchor),
            qrImageView.widthAnchor.constraint(equalToConstant: 200),
            qrImageView.heightAnchor.constraint(equalToConstant: 200),
        ])

        // Set preview container to 45% of view height
        previewContainer.heightAnchor.constraint(equalTo: view.safeAreaLayoutGuide.heightAnchor, multiplier: 0.45).isActive = true
    }

    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        for sublayer in previewContainer.layer.sublayers ?? [] {
            if let layer = sublayer as? AVCaptureVideoPreviewLayer {
                layer.frame = previewContainer.bounds
            }
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        if isStreaming { stopStream() }
        cameraManager.stopSession()
        streamServer.stop()
    }
}

package com.rifatcam.pro

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.util.Log
import android.view.ScaleGestureDetector
import android.view.View
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.zxing.integration.android.IntentIntegrator
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class MainActivity : AppCompatActivity() {

    private lateinit var previewView: PreviewView
    private lateinit var cameraManager: CameraManager
    private lateinit var streamServer: StreamServer
    private lateinit var powerManager: PowerManager
    private var wakeLock: PowerManager.WakeLock? = null

    private lateinit var btnStartStop: Button
    private lateinit var btnSwitchCamera: ImageButton
    private lateinit var btnFlash: ImageButton
    private lateinit var btnQR: ImageButton
    private lateinit var statusText: TextView
    private lateinit var urlText: TextView
    private lateinit var qrImage: ImageView
    private lateinit var clientCountText: TextView
    private lateinit var resolutionSpinner: Spinner
    private lateinit var zoomSeekBar: SeekBar

    private var isStreaming = false
    private var discoveryJob: Job? = null
    private var currentZoom = 1.0f

    private val tag = "RifatCam-Main"

    private val requiredPermissions = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.POST_NOTIFICATIONS
    )

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            initializeCamera()
        } else {
            Toast.makeText(this, "Camera permission is required", Toast.LENGTH_LONG).show()
            finish()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initializeViews()
        setupControls()
        checkPermissions()
    }

    private fun initializeViews() {
        previewView = findViewById(R.id.previewView)
        btnStartStop = findViewById(R.id.btnStartStop)
        btnSwitchCamera = findViewById(R.id.btnSwitchCamera)
        btnFlash = findViewById(R.id.btnFlash)
        btnQR = findViewById(R.id.btnQR)
        statusText = findViewById(R.id.statusText)
        urlText = findViewById(R.id.urlText)
        qrImage = findViewById(R.id.qrImage)
        clientCountText = findViewById(R.id.clientCountText)
        resolutionSpinner = findViewById(R.id.resolutionSpinner)
        zoomSeekBar = findViewById(R.id.zoomSeekBar)

        val streamResolutions = arrayOf("480p (640x480)", "720p (1280x720)", "1080p (1920x1080)")
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, streamResolutions)
        resolutionSpinner.adapter = adapter
        resolutionSpinner.setSelection(1)
    }

    private fun setupControls() {
        btnStartStop.setOnClickListener {
            if (isStreaming) {
                stopStream()
            } else {
                startStream()
            }
        }

        btnSwitchCamera.setOnClickListener {
            cameraManager.switchCamera()
            updateFlashButton()
        }

        btnFlash.setOnClickListener {
            val enabled = cameraManager.toggleFlash()
            updateFlashButton(enabled)
        }

        btnQR.setOnClickListener {
            showQRCode()
        }

        resolutionSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>, view: View?, pos: Int, id: Long) {
                val res = when (pos) {
                    0 -> android.util.Size(640, 480)
                    1 -> android.util.Size(1280, 720)
                    2 -> android.util.Size(1920, 1080)
                    else -> android.util.Size(1280, 720)
                }
                cameraManager.setResolution(res.width, res.height)
            }

            override fun onNothingSelected(parent: AdapterView<*>) {}
        }

        zoomSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser) {
                    currentZoom = 1.0f + (progress / 100.0f) * 4.0f
                    cameraManager.setZoom(currentZoom)
                }
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })
    }

    private fun checkPermissions() {
        val needed = requiredPermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (needed.isEmpty()) {
            initializeCamera()
        } else {
            permissionLauncher.launch(needed.toTypedArray())
        }
    }

    private fun initializeCamera() {
        cameraManager = CameraManager(this, this)
        cameraManager.setPreviewView(previewView)
        cameraManager.startCamera()

        streamServer = StreamServer(
            port = NetworkUtils.STREAM_PORT,
            deviceName = "RifatCam Phone"
        )

        powerManager = getSystemService(POWER_SERVICE) as PowerManager

        val ip = NetworkUtils.getLocalIpAddress(this)
        urlText.text = "http://$ip:${NetworkUtils.STREAM_PORT}"

        updateStatus("Ready", "#00ff88")
        updateClientCount(0)
    }

    private fun startStream() {
        if (!NetworkUtils.isWifiConnected(this)) {
            Toast.makeText(this, "Wi-Fi is required for streaming", Toast.LENGTH_LONG).show()
            return
        }

        cameraManager.setFrameListener(object : CameraManager.CameraFrameListener {
            override fun onFrame(jpegData: ByteArray, width: Int, height: Int) {
                streamServer.setFrameProvider(object : StreamServer.FrameProvider {
                    override fun getLatestJpeg(): ByteArray? = jpegData

                    override fun getInfoJson(): String = cameraManager.getInfoJson()
                })
            }
        })

        cameraManager.startStreaming()
        streamServer.start()

        isStreaming = true
        btnStartStop.text = "■ STOP STREAM"
        btnStartStop.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_red_dark))
        updateStatus("STREAMING LIVE", "#ff3366")

        val ip = NetworkUtils.getLocalIpAddress(this)
        val streamUrl = "http://$ip:${NetworkUtils.STREAM_PORT}"
        urlText.text = streamUrl

        startDiscoveryListener()

        // Keep screen on
        wakeLock = powerManager.newWakeLock(
            PowerManager.SCREEN_DIM_WAKE_LOCK,
            "RifatCam:StreamWakeLock"
        )
        wakeLock?.acquire(3 * 60 * 60 * 1000L) // 3 hours max

        // Start foreground service
        val serviceIntent = Intent(this, CameraStreamService::class.java).apply {
            action = CameraStreamService.ACTION_START_STREAM
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }

    private fun stopStream() {
        cameraManager.stopStreaming()
        streamServer.stop()

        isStreaming = false
        btnStartStop.text = "● START STREAM"
        btnStartStop.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_blue_dark))
        updateStatus("Ready", "#00ff88")
        updateClientCount(0)

        discoveryJob?.cancel()

        wakeLock?.release()
        wakeLock = null

        // Stop foreground service
        val serviceIntent = Intent(this, CameraStreamService::class.java).apply {
            action = CameraStreamService.ACTION_STOP_STREAM
        }
        stopService(serviceIntent)
    }

    private fun startDiscoveryListener() {
        discoveryJob = lifecycleScope.launch(Dispatchers.IO) {
            val socket = DatagramSocket(NetworkUtils.DISCOVERY_PORT)
            socket.broadcast = true
            socket.soTimeout = 1000
            val buffer = ByteArray(1024)

            try {
                while (isActive && isStreaming) {
                    try {
                        val packet = DatagramPacket(buffer, buffer.size)
                        socket.receive(packet)
                        val message = String(packet.data, 0, packet.length, Charsets.UTF_8)

                        if (message == NetworkUtils.DISCOVERY_MAGIC) {
                            val ip = NetworkUtils.getLocalIpAddress(this@MainActivity)
                            val responseBody = """{"name":"RifatCam Phone","port":${NetworkUtils.STREAM_PORT},"device_id":"android-1","protocol":"mjpeg"}"""
                            val response = NetworkUtils.DISCOVERY_RESPONSE + responseBody
                            val responsePacket = DatagramPacket(
                                response.toByteArray(),
                                response.length,
                                packet.address,
                                packet.port
                            )
                            socket.send(responsePacket)
                            Log.d(tag, "Discovery response sent to ${packet.address}")
                        }
                    } catch (e: Exception) {
                        // Timeout or other error
                    }

                    withContext(Dispatchers.Main) {
                        val clients = streamServer.getClientCount()
                        updateClientCount(clients)
                    }

                    delay(1000)
                }
            } catch (e: Exception) {
                Log.e(tag, "Discovery error: ${e.message}")
            } finally {
                socket.close()
            }
        }
    }

    private fun showQRCode() {
        val ip = NetworkUtils.getLocalIpAddress(this)
        val qrContent = QRCodeHelper.generateStreamQRContent(
            ipAddress = ip,
            port = NetworkUtils.STREAM_PORT,
            deviceName = "RifatCam Phone"
        )

        lifecycleScope.launch(Dispatchers.IO) {
            val bitmap = QRCodeHelper.generateQRCode(qrContent)
            withContext(Dispatchers.Main) {
                if (bitmap != null) {
                    qrImage.setImageBitmap(bitmap)
                    qrImage.visibility = View.VISIBLE
                    Toast.makeText(
                        this@MainActivity,
                        "Scan QR code with RifatCam Desktop",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }

    private fun updateStatus(status: String, color: String) {
        runOnUiThread {
            statusText.text = "● $status"
            try {
                val colorInt = android.graphics.Color.parseColor(color)
                statusText.setTextColor(colorInt)
            } catch (e: Exception) {
                statusText.setTextColor(android.graphics.Color.parseColor("#00ff88"))
            }
        }
    }

    private fun updateClientCount(count: Int) {
        runOnUiThread {
            clientCountText.text = "Connected: $count client${if (count != 1) "s" else ""}"
        }
    }

    private fun updateFlashButton(enabled: Boolean? = null) {
        val isEnabled = enabled ?: cameraManager.isFlashEnabled()
        runOnUiThread {
            btnFlash.alpha = if (isEnabled) 1.0f else 0.4f
        }
    }

    override fun onDestroy() {
        if (isStreaming) {
            stopStream()
        }
        cameraManager.release()
        streamServer.stop()
        super.onDestroy()
    }
}

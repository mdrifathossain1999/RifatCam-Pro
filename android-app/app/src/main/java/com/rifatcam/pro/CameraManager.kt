package com.rifatcam.pro

import android.Manifest
import android.content.Context
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import android.util.Log
import android.util.Size
import android.view.Surface
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.Executors

class CameraManager(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner
) {
    interface CameraFrameListener {
        fun onFrame(jpegData: ByteArray, width: Int, height: Int)
    }

    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var cameraSelector: CameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
    private var imageCapture: ImageCapture? = null
    private var preview: Preview? = null
    private var lensFacing = CameraSelector.LENS_FACING_BACK
    private var flashEnabled = false
    private var isStreaming = false
    private var frameListener: CameraFrameListener? = null
    private var previewView: PreviewView? = null
    private var targetResolution = Size(1280, 720) // 720p default

    private val executor = Executors.newSingleThreadExecutor()
    private val tag = "CameraManager"

    fun setFrameListener(listener: CameraFrameListener) {
        this.frameListener = listener
    }

    fun setPreviewView(view: PreviewView) {
        this.previewView = view
    }

    fun setResolution(width: Int, height: Int) {
        targetResolution = Size(width, height)
    }

    fun isBackCamera(): Boolean = lensFacing == CameraSelector.LENS_FACING_BACK

    fun isFlashEnabled(): Boolean = flashEnabled

    fun isStreaming(): Boolean = isStreaming

    fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProviderFuture.addListener({
            try {
                cameraProvider = cameraProviderFuture.get()
                bindCamera()
            } catch (e: Exception) {
                Log.e(tag, "Camera init failed: ${e.message}")
            }
        }, ContextCompat.getMainExecutor(context))
    }

    private fun bindCamera() {
        val provider = cameraProvider ?: return

        provider.unbindAll()

        preview = Preview.Builder()
            .setTargetResolution(targetResolution)
            .build()

        preview?.setSurfaceProvider(previewView?.surfaceProvider)

        imageCapture = ImageCapture.Builder()
            .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
            .setTargetResolution(targetResolution)
            .setTargetRotation(Surface.ROTATION_0)
            .build()

        cameraSelector = if (lensFacing == CameraSelector.LENS_FACING_BACK) {
            CameraSelector.DEFAULT_BACK_CAMERA
        } else {
            CameraSelector.DEFAULT_FRONT_CAMERA
        }

        try {
            camera = provider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageCapture
            )

            val cam = camera
            if (cam != null) {
                cam.cameraInfo.cameraState.observe(lifecycleOwner) { state ->
                    Log.d(tag, "Camera state: ${state.type}")
                }
            }

            if (flashEnabled && isBackCamera()) {
                camera?.cameraControl?.enableTorch(true)
            }

            Log.i(tag, "Camera bound successfully")
        } catch (e: Exception) {
            Log.e(tag, "Camera bind failed: ${e.message}")
        }
    }

    fun switchCamera() {
        lensFacing = if (lensFacing == CameraSelector.LENS_FACING_BACK) {
            CameraSelector.LENS_FACING_FRONT
        } else {
            CameraSelector.LENS_FACING_BACK
        }
        flashEnabled = false
        bindCamera()
    }

    fun toggleFlash(): Boolean {
        if (!isBackCamera()) return false
        flashEnabled = !flashEnabled
        camera?.cameraControl?.enableTorch(flashEnabled)
        return flashEnabled
    }

    fun setZoom(ratio: Float) {
        camera?.cameraControl?.setZoomRatio(ratio)
    }

    fun startStreaming() {
        if (isStreaming) return
        if (imageCapture == null) {
            Log.w(tag, "ImageCapture not initialized")
            return
        }
        isStreaming = true

        val capture = imageCapture ?: return

        // Use ImageAnalysis for streaming frames
        val imageAnalysis = ImageAnalysis.Builder()
            .setTargetResolution(targetResolution)
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()

        imageAnalysis.setAnalyzer(executor) { imageProxy ->
            if (!isStreaming) {
                imageProxy.close()
                return@setAnalyzer
            }

            try {
                val jpegData = imageToJpeg(imageProxy)
                imageProxy.close()

                if (jpegData != null) {
                    frameListener?.onFrame(jpegData, targetResolution.width, targetResolution.height)
                }
            } catch (e: Exception) {
                imageProxy.close()
            }
        }

        val provider = cameraProvider ?: return
        provider.unbindAll()

        preview = Preview.Builder()
            .setTargetResolution(targetResolution)
            .build()
        preview?.setSurfaceProvider(previewView?.surfaceProvider)

        try {
            camera = provider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalysis,
                imageCapture
            )
            Log.i(tag, "Streaming started with ImageAnalysis")
        } catch (e: Exception) {
            Log.e(tag, "Failed to bind analysis: ${e.message}")
        }
    }

    fun stopStreaming() {
        isStreaming = false
        // Re-bind without analysis to save battery
        bindCamera()
        Log.i(tag, "Streaming stopped")
    }

    fun release() {
        isStreaming = false
        cameraProvider?.unbindAll()
        cameraProvider?.shutdown()
        executor.shutdown()
    }

    private fun imageToJpeg(imageProxy: ImageProxy): ByteArray? {
        return try {
            when (imageProxy.format) {
                ImageFormat.YUV_420_888,
                ImageFormat.NV21 -> {
                    val buffer: ByteBuffer = imageProxy.planes[0].buffer
                    val ySize = buffer.remaining()
                    val uvBuffer: ByteBuffer = imageProxy.planes[2].buffer
                    val uvSize = uvBuffer.remaining()

                    val nv21 = ByteArray(ySize + uvSize)
                    buffer.get(nv21, 0, ySize)
                    uvBuffer.get(nv21, ySize, uvSize)

                    val yuvImage = YuvImage(
                        nv21,
                        ImageFormat.NV21,
                        imageProxy.width,
                        imageProxy.height,
                        null
                    )
                    val out = ByteArrayOutputStream()
                    yuvImage.compressToJpeg(
                        Rect(0, 0, imageProxy.width, imageProxy.height),
                        85,
                        out
                    )
                    out.toByteArray()
                }
                ImageFormat.JPEG -> {
                    val buffer = imageProxy.planes[0].buffer
                    val bytes = ByteArray(buffer.remaining())
                    buffer.get(bytes)
                    bytes
                }
                else -> {
                    // Fallback: use capture
                    imageProxyToJpegFallback(imageProxy)
                }
            }
        } catch (e: Exception) {
            Log.e(tag, "Image to JPEG error: ${e.message}")
            null
        }
    }

    private fun imageProxyToJpegFallback(imageProxy: ImageProxy): ByteArray? {
        // This is a simplified fallback
        try {
            val buffer = imageProxy.planes[0].buffer
            val bytes = ByteArray(buffer.remaining())
            buffer.get(bytes)
            return bytes
        } catch (e: Exception) {
            return null
        }
    }

    fun getInfoJson(): String {
        val cameraType = if (isBackCamera()) "back" else "front"
        val res = targetResolution
        return """
        {
            "status": "streaming",
            "name": "RifatCam Phone",
            "device_id": "android-1",
            "protocol": "mjpeg",
            "camera": "$cameraType",
            "resolution": "${res.width}x${res.height}",
            "flash": $flashEnabled,
            "clients": 0
        }
        """.trimIndent()
    }
}

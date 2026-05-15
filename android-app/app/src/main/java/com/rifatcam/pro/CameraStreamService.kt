package com.rifatcam.pro

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat

class CameraStreamService : Service() {

    private val tag = "CameraStreamService"
    private var streamServer: StreamServer? = null
    private var cameraManager: CameraManager? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()

        when (intent?.action) {
            ACTION_START_STREAM -> {
                startForeground(NOTIFICATION_ID, notification)
                startStreaming()
            }
            ACTION_STOP_STREAM -> {
                stopStreaming()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
            ACTION_UPDATE_SETTINGS -> {
                updateNotification("Streaming active")
            }
            else -> {
                // If service is restarted, just show notification
                startForeground(NOTIFICATION_ID, notification)
            }
        }

        return START_STICKY
    }

    private fun startStreaming() {
        Log.i(tag, "Starting background streaming service")

        streamServer = StreamServer(
            port = NetworkUtils.STREAM_PORT,
            deviceName = "RifatCam Phone"
        )

        streamServer?.start()
    }

    fun setCameraManager(manager: CameraManager) {
        this.cameraManager = manager
        streamServer?.setFrameProvider(object : StreamServer.FrameProvider {
            override fun getLatestJpeg(): ByteArray? {
                return null // Camera provides frames via listener, not through service directly
            }

            override fun getInfoJson(): String {
                return cameraManager?.getInfoJson() ?: """{"status":"idle"}"""
            }
        })
    }

    fun setStreamServer(server: StreamServer) {
        this.streamServer = server
    }

    private fun stopStreaming() {
        Log.i(tag, "Stopping streaming service")
        streamServer?.stop()
        streamServer = null
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        stopStreaming()
        super.onDestroy()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Camera Stream",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Background camera streaming service"
                setShowBadge(false)
                enableVibration(false)
                enableLights(false)
            }
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val stopIntent = PendingIntent.getService(
            this,
            1,
            Intent(this, CameraStreamService::class.java).apply {
                action = ACTION_STOP_STREAM
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("RifatCam Pro")
            .setContentText("Streaming active")
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setContentIntent(pendingIntent)
            .addAction(android.R.drawable.ic_media_pause, "Stop", stopIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setSilent(true)
            .build()
    }

    private fun updateNotification(text: String) {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("RifatCam Pro")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    companion object {
        const val CHANNEL_ID = "rifatcam_stream_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_START_STREAM = "com.rifatcam.pro.START_STREAM"
        const val ACTION_STOP_STREAM = "com.rifatcam.pro.STOP_STREAM"
        const val ACTION_UPDATE_SETTINGS = "com.rifatcam.pro.UPDATE_SETTINGS"
    }
}

package com.rifatcam.pro

import android.graphics.Bitmap
import com.google.zxing.BarcodeFormat
import com.google.zxing.MultiFormatWriter
import com.google.zxing.WriterException
import com.google.zxing.common.BitMatrix

object QRCodeHelper {

    private const val QR_SIZE = 512
    private const val WHITE = -0x1
    private const val BLACK = -0x1000000

    fun generateQRCode(content: String): Bitmap? {
        return try {
            val writer = MultiFormatWriter()
            val bitMatrix: BitMatrix = writer.encode(
                content,
                BarcodeFormat.QR_CODE,
                QR_SIZE,
                QR_SIZE
            )

            val bitmap = Bitmap.createBitmap(QR_SIZE, QR_SIZE, Bitmap.Config.RGB_565)
            for (x in 0 until QR_SIZE) {
                for (y in 0 until QR_SIZE) {
                    bitmap.setPixel(
                        x, y,
                        if (bitMatrix[x, y]) BLACK else WHITE
                    )
                }
            }
            bitmap
        } catch (e: WriterException) {
            e.printStackTrace()
            null
        }
    }

    fun generateStreamQRContent(ipAddress: String, port: Int, deviceName: String): String {
        return "rifatcam://connect?ip=$ipAddress&port=$port&name=$deviceName"
    }

    data class QRConnectionData(
        val ip: String,
        val port: Int,
        val name: String
    )

    fun parseQRContent(content: String): QRConnectionData? {
        return try {
            if (!content.startsWith("rifatcam://connect?")) return null
            val query = content.removePrefix("rifatcam://connect?")
            val params = query.split("&").associate {
                val parts = it.split("=", limit = 2)
                parts[0] to (parts.getOrNull(1) ?: "")
            }
            QRConnectionData(
                ip = params["ip"] ?: return null,
                port = params["port"]?.toIntOrNull() ?: NetworkUtils.STREAM_PORT,
                name = params["name"] ?: "RifatCam Device"
            )
        } catch (e: Exception) {
            null
        }
    }
}

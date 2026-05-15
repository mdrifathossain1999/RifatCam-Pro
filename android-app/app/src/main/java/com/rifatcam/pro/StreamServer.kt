package com.rifatcam.pro

import android.util.Log
import org.json.JSONObject
import java.io.IOException
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket
import java.net.URLDecoder
import java.nio.charset.StandardCharsets

class StreamServer(
    private val port: Int = NetworkUtils.STREAM_PORT,
    private val deviceName: String = "RifatCam"
) {
    interface FrameProvider {
        fun getLatestJpeg(): ByteArray?
        fun getInfoJson(): String
    }

    private var serverSocket: ServerSocket? = null
    private var running = false
    private var frameProvider: FrameProvider? = null
    private val clients = mutableListOf<ClientHandler>()
    private val tag = "StreamServer"

    fun setFrameProvider(provider: FrameProvider) {
        this.frameProvider = provider
    }

    fun start() {
        if (running) return
        running = true
        Thread({ serverLoop() }, "stream-server").apply {
            isDaemon = true
            start()
        }
        Log.i(tag, "Stream server started on port $port")
    }

    fun stop() {
        running = false
        try {
            serverSocket?.close()
        } catch (e: IOException) {
            // ignore
        }
        synchronized(clients) {
            for (client in clients) {
                client.stop()
            }
            clients.clear()
        }
        Log.i(tag, "Stream server stopped")
    }

    fun getClientCount(): Int {
        synchronized(clients) {
            return clients.size
        }
    }

    private fun serverLoop() {
        try {
            serverSocket = ServerSocket()
            serverSocket?.reuseAddress = true
            serverSocket?.bind(InetSocketAddress(port))
            Log.i(tag, "Server listening on 0.0.0.0:$port")

            while (running) {
                try {
                    val clientSocket = serverSocket?.accept() ?: continue
                    clientSocket.soTimeout = 10000
                    val handler = ClientHandler(clientSocket)
                    synchronized(clients) {
                        clients.add(handler)
                    }
                    handler.start()
                    Log.d(tag, "Client connected: ${clientSocket.inetAddress.hostAddress}")
                } catch (e: IOException) {
                    if (running) {
                        Log.e(tag, "Accept error: ${e.message}")
                    }
                }
            }
        } catch (e: IOException) {
            if (running) {
                Log.e(tag, "Server error: ${e.message}")
            }
        }
    }

    inner class ClientHandler(private val socket: Socket) : Thread("stream-client") {
        private var clientRunning = true

        fun stopClient() {
            clientRunning = false
            try {
                socket.close()
            } catch (e: IOException) {
                // ignore
            }
        }

        override fun run() {
            try {
                val inputStream = socket.getInputStream()
                val outputStream = socket.getOutputStream()

                val request = readRequest(inputStream)

                if (request == null) {
                    sendError(outputStream, 400, "Bad Request")
                    return
                }

                when {
                    request.startsWith("GET /video") -> handleVideoStream(outputStream)
                    request.startsWith("GET /info") -> handleInfo(outputStream)
                    request.startsWith("POST /control") -> {
                        val body = readBody(inputStream, request)
                        handleControl(outputStream, body)
                    }
                    request.startsWith("GET /") -> handleIndex(outputStream)
                    else -> sendError(outputStream, 404, "Not Found")
                }
            } catch (e: IOException) {
                Log.d(tag, "Client disconnected: ${e.message}")
            } finally {
                try {
                    socket.close()
                } catch (e: IOException) {
                    // ignore
                }
                synchronized(clients) {
                    clients.remove(this)
                }
            }
        }

        private fun readRequest(inputStream: java.io.InputStream): String? {
            try {
                val buffer = ByteArray(4096)
                val bytesRead = inputStream.read(buffer)
                if (bytesRead <= 0) return null
                val request = String(buffer, 0, bytesRead, StandardCharsets.UTF_8)
                val headerEnd = request.indexOf("\r\n")
                return if (headerEnd >= 0) request.substring(0, headerEnd) else null
            } catch (e: Exception) {
                return null
            }
        }

        private fun readBody(inputStream: java.io.InputStream, request: String): String {
            val contentLength = request.lines().find { it.lowercase().startsWith("content-length:") }
                ?.split(":")?.get(1)?.trim()?.toIntOrNull() ?: return "{}"
            try {
                val body = ByteArray(contentLength)
                var totalRead = 0
                while (totalRead < contentLength) {
                    val read = inputStream.read(body, totalRead, contentLength - totalRead)
                    if (read == -1) break
                    totalRead += read
                }
                return String(body, 0, totalRead, StandardCharsets.UTF_8)
            } catch (e: Exception) {
                return "{}"
            }
        }

        private fun handleVideoStream(outputStream: OutputStream) {
            val boundary = "--boundary"
            val contentType = "multipart/x-mixed-replace; boundary=$boundary"

            sendHeaders(outputStream, 200, contentType)

            val boundaryBytes = "--$boundary\r\n".toByteArray()
            val headerTemplate = "Content-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n"

            while (clientRunning && running) {
                val jpegData = frameProvider?.getLatestJpeg()
                if (jpegData != null) {
                    try {
                        outputStream.write(boundaryBytes)
                        outputStream.write(headerTemplate.format(jpegData.size).toByteArray())
                        outputStream.write(jpegData)
                        outputStream.write("\r\n".toByteArray())
                        outputStream.flush()
                    } catch (e: IOException) {
                        break
                    }
                } else {
                    try {
                        Thread.sleep(30)
                    } catch (e: InterruptedException) {
                        break
                    }
                }
            }
        }

        private fun handleInfo(outputStream: OutputStream) {
            val info = frameProvider?.getInfoJson() ?: """{"status":"active","name":"$deviceName","port":$port}"""
            val body = info.toByteArray()
            sendHeaders(outputStream, 200, "application/json", body.size)
            outputStream.write(body)
            outputStream.flush()
        }

        private fun handleControl(outputStream: OutputStream, body: String) {
            try {
                val json = JSONObject(body)
                val command = json.optString("command", "")
                Log.d(tag, "Control command: $command")
                val response = """{"status":"ok","command":"$command"}"""
                val responseBytes = response.toByteArray()
                sendHeaders(outputStream, 200, "application/json", responseBytes.size)
                outputStream.write(responseBytes)
            } catch (e: Exception) {
                sendError(outputStream, 400, "Invalid JSON")
            }
        }

        private fun handleIndex(outputStream: OutputStream) {
            val html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>RifatCam Pro - $deviceName</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { background: #0a0e17; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
                        h1 { color: #00d4ff; font-size: 24px; margin-bottom: 20px; letter-spacing: 3px; }
                        img { width: 100%; max-width: 720px; border: 1px solid rgba(0,212,255,0.3); border-radius: 12px; }
                        .info { margin-top: 20px; color: #8899aa; font-size: 14px; }
                        .status { color: #00ff88; margin-top: 10px; }
                    </style>
                </head>
                <body>
                    <h1>◆ RIFATCAM PRO</h1>
                    <img src="/video" alt="Live Stream" />
                    <div class="info">Device: $deviceName | Port: $port</div>
                    <div class="status">● LIVE</div>
                </body>
                </html>
            """.trimIndent()
            val body = html.toByteArray()
            sendHeaders(outputStream, 200, "text/html", body.size)
            outputStream.write(body)
            outputStream.flush()
        }

        private fun sendHeaders(outputStream: OutputStream, statusCode: Int, contentType: String, contentLength: Int = -1) {
            val reason = when (statusCode) {
                200 -> "OK"
                400 -> "Bad Request"
                404 -> "Not Found"
                500 -> "Internal Server Error"
                else -> "Unknown"
            }
            val headers = StringBuilder()
            headers.append("HTTP/1.0 $statusCode $reason\r\n")
            headers.append("Content-Type: $contentType\r\n")
            headers.append("Connection: close\r\n")
            headers.append("Cache-Control: no-cache, no-store, must-revalidate\r\n")
            headers.append("Pragma: no-cache\r\n")
            headers.append("Access-Control-Allow-Origin: *\r\n")
            if (contentLength >= 0) {
                headers.append("Content-Length: $contentLength\r\n")
            }
            headers.append("\r\n")
            outputStream.write(headers.toString().toByteArray())
            outputStream.flush()
        }

        private fun sendError(outputStream: OutputStream, statusCode: Int, message: String) {
            val body = """{"error":"$message"}"""
            sendHeaders(outputStream, statusCode, "application/json", body.length)
            outputStream.write(body.toByteArray())
            outputStream.flush()
        }
    }
}

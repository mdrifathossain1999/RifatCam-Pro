import UIKit

class StreamServer {
    private var serverFd: Int32 = -1
    private var running = false
    private var clients: Set<Int32> = []
    private let clientsLock = NSLock()
    private let serverQueue = DispatchQueue(label: "stream.server.queue", qos: .userInitiated)
    private var latestJPEG: Data?
    private let jpegLock = NSLock()

    var deviceName = "RifatCam iPhone"
    var port: UInt16 = NetworkUtils.streamPort

    func updateJPEG(_ data: Data) {
        jpegLock.lock()
        latestJPEG = data
        jpegLock.unlock()
    }

    func start() {
        guard !running else { return }
        running = true

        serverQueue.async { [weak self] in
            self?.runServer()
        }
    }

    func stop() {
        running = false
        clientsLock.lock()
        for fd in clients {
            close(fd)
        }
        clients.removeAll()
        clientsLock.unlock()
        if serverFd >= 0 {
            close(serverFd)
            serverFd = -1
        }
    }

    var clientCount: Int {
        clientsLock.lock()
        let count = clients.count
        clientsLock.unlock()
        return count
    }

    private func runServer() {
        serverFd = Darwin.socket(AF_INET, SOCK_STREAM, 0)
        guard serverFd >= 0 else { print("[Server] socket() failed"); return }

        var opt: Int = 1
        setsockopt(serverFd, SOL_SOCKET, SO_REUSEADDR, &opt, socklen_t(MemoryLayout.size(ofValue: opt)))

        var addr = sockaddr_in()
        addr.sin_family = sa_family_t(AF_INET)
        addr.sin_port = CFSwapInt16HostToBig(port)
        addr.sin_addr.s_addr = INADDR_ANY
        addr.sin_len = UInt8(MemoryLayout<sockaddr_in>.size)

        let bindResult = withUnsafePointer(to: &addr) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                Darwin.bind(serverFd, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }

        guard bindResult == 0 else {
            print("[Server] bind() failed on port \(port)")
            close(serverFd)
            serverFd = -1
            return
        }

        listen(serverFd, 5)
        print("[Server] Listening on port \(port)")

        while running {
            var clientAddr = sockaddr_in()
            var addrLen = socklen_t(MemoryLayout<sockaddr_in>.size)
            let clientFd = withUnsafeMutablePointer(to: &clientAddr) {
                $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                    Darwin.accept(serverFd, $0, &addrLen)
                }
            }

            guard clientFd >= 0 else {
                if running { print("[Server] accept() error") }
                break
            }

            clientsLock.lock()
            clients.insert(clientFd)
            clientsLock.unlock()

            DispatchQueue.global(qos: .default).async { [weak self] in
                self?.handleClient(clientFd)
            }
        }

        close(serverFd)
        serverFd = -1
        print("[Server] Stopped")
    }

    private func handleClient(_ fd: Int32) {
        defer {
            close(fd)
            clientsLock.lock()
            clients.remove(fd)
            clientsLock.unlock()
        }

        var buffer = [UInt8](repeating: 0, count: 4096)
        let bytesRead = read(fd, &buffer, 4096)
        guard bytesRead > 0 else { return }

        let request = String(bytes: buffer[0..<min(bytesRead, 4096)], encoding: .utf8) ?? ""
        let lines = request.components(separatedBy: "\r\n")
        guard let firstLine = lines.first else { return }

        if firstLine.hasPrefix("GET /video") {
            handleVideoStream(fd)
        } else if firstLine.hasPrefix("GET /info") {
            handleInfo(fd)
        } else if firstLine.hasPrefix("POST /control") {
            handleControl(fd, request: request)
        } else if firstLine.hasPrefix("GET / ") || firstLine == "GET / HTTP/1.0" || firstLine == "GET / HTTP/1.1" {
            handleIndex(fd)
        } else {
            sendResponse(fd, statusCode: 404, contentType: "text/plain", body: "Not Found")
        }
    }

    private func handleVideoStream(_ fd: Int32) {
        let headers = "HTTP/1.0 200 OK\r\n" +
            "Content-Type: multipart/x-mixed-replace; boundary=--boundary\r\n" +
            "Cache-Control: no-cache, no-store, must-revalidate\r\n" +
            "Pragma: no-cache\r\n" +
            "Connection: close\r\n" +
            "Access-Control-Allow-Origin: *\r\n\r\n"
        writeString(fd, headers)

        let boundaryPrefix = "--boundary\r\n" +
            "Content-Type: image/jpeg\r\n" +
            "Content-Length: %d\r\n\r\n"

        while running {
            var jpeg: Data?
            jpegLock.lock()
            jpeg = latestJPEG
            jpegLock.unlock()

            if let data = jpeg {
                let header = String(format: boundaryPrefix, data.count)
                writeString(fd, header)
                data.withUnsafeBytes { ptr in
                    if let base = ptr.baseAddress {
                        _ = write(fd, base, data.count)
                    }
                }
                writeString(fd, "\r\n")
            } else {
                Thread.sleep(forTimeInterval: 0.03)
            }
        }
    }

    private func handleInfo(_ fd: Int32) {
        let ip = NetworkUtils.getWiFiAddress() ?? "unknown"
        let json = """
        {"status":"streaming","name":"\(deviceName)","device_id":"ios-1","protocol":"mjpeg","ip":"\(ip)","port":\(port)}
        """
        sendResponse(fd, statusCode: 200, contentType: "application/json", body: json)
    }

    private func handleControl(_ fd: Int32, request: String) {
        let body = request.components(separatedBy: "\r\n\r\n").last ?? "{}"
        let response = "{\"status\":\"ok\",\"received\":\(body.count > 0 ? "true" : "false")}"
        sendResponse(fd, statusCode: 200, contentType: "application/json", body: response)
    }

    private func handleIndex(_ fd: Int32) {
        let ip = NetworkUtils.getWiFiAddress() ?? "localhost"
        let html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RifatCam Pro - \(deviceName)</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin:0; padding:0; box-sizing:border-box; }
                body { background:#0a0e17; color:#fff; font-family:-apple-system, sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; }
                h1 { color:#00d4ff; font-size:22px; letter-spacing:3px; margin-bottom:16px; }
                img { width:100%%; max-width:720px; border:1px solid rgba(0,212,255,0.3); border-radius:12px; }
                .info { color:#8899aa; font-size:13px; margin-top:16px; }
                .status { color:#00ff88; font-size:14px; margin-top:8px; }
            </style>
        </head>
        <body>
            <h1>&#9670; RIFATCAM PRO</h1>
            <img src="/video" alt="Live Stream" />
            <div class="info">Device: \(deviceName) | \(ip):\(port)</div>
            <div class="status">&#9679; LIVE</div>
        </body>
        </html>
        """
        sendResponse(fd, statusCode: 200, contentType: "text/html", body: html)
    }

    private func sendResponse(_ fd: Int32, statusCode: Int, contentType: String, body: String) {
        let reason = statusCode == 200 ? "OK" : statusCode == 404 ? "Not Found" : "Unknown"
        let response = "HTTP/1.0 \(statusCode) \(reason)\r\n" +
            "Content-Type: \(contentType)\r\n" +
            "Content-Length: \(body.utf8.count)\r\n" +
            "Connection: close\r\n" +
            "Access-Control-Allow-Origin: *\r\n\r\n" +
            body
        writeString(fd, response)
    }

    private func writeString(_ fd: Int32, _ string: String) {
        let data = string.data(using: .utf8)!
        data.withUnsafeBytes { ptr in
            if let base = ptr.baseAddress {
                _ = write(fd, base, data.count)
            }
        }
    }
}

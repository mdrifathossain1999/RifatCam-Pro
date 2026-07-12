import Foundation

struct NetworkUtils {
    static let streamPort: UInt16 = 8080

    static func getWiFiAddress() -> String? {
        var address: String?
        var ifaddr: UnsafeMutablePointer<ifaddrs>? = nil
        guard getifaddrs(&ifaddr) == 0, let firstAddr = ifaddr else { return nil }

        var ptr = firstAddr
        while true {
            let interface = ptr.pointee
            guard let ifaAddr = interface.ifa_addr else {
                guard let next = interface.ifa_next else { break }
                ptr = next
                continue
            }
            let addrFamily = ifaAddr.pointee.sa_family
            if addrFamily == sa_family_t(AF_INET) {
                let name = String(cString: interface.ifa_name)
                if name == "en0" {
                    var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
                    getnameinfo(ifaAddr, socklen_t(ifaAddr.pointee.sa_len),
                               &hostname, socklen_t(hostname.count), nil, 0, NI_NUMERICHOST)
                    address = String(cString: hostname)
                }
            }
            guard let next = interface.ifa_next else { break }
            ptr = next
        }
        freeifaddrs(ifaddr)
        return address
    }

    static func getStreamURL() -> URL? {
        guard let ip = getWiFiAddress() else { return nil }
        return URL(string: "http://\(ip):\(streamPort)/video")
    }

    static func getInfoURL() -> URL? {
        guard let ip = getWiFiAddress() else { return nil }
        return URL(string: "http://\(ip):\(streamPort)/info")
    }

    static func getBaseURLString() -> String {
        guard let ip = getWiFiAddress() else { return "http://localhost:\(streamPort)" }
        return "http://\(ip):\(streamPort)"
    }

    static func isWifiConnected() -> Bool {
        guard let ip = getWiFiAddress() else { return false }
        return !ip.isEmpty && ip != "127.0.0.1"
    }
}

import UIKit
import CoreImage

struct QRCodeHelper {
    static func generateQRCode(from string: String) -> UIImage? {
        let data = string.data(using: .utf8)
        guard let filter = CIFilter(name: "CIQRCodeGenerator") else { return nil }
        filter.setValue(data, forKey: "inputMessage")
        filter.setValue("H", forKey: "inputCorrectionLevel")
        guard let ciImage = filter.outputImage else { return nil }

        let scale: CGFloat = 10
        let transform = CGAffineTransform(scaleX: scale, y: scale)
        let scaledCIImage = ciImage.transformed(by: transform)

        let context = CIContext()
        guard let cgImage = context.createCGImage(scaledCIImage, from: scaledCIImage.extent) else { return nil }
        return UIImage(cgImage: cgImage)
    }

    static func generateStreamQRContent() -> String {
        guard let ip = NetworkUtils.getWiFiAddress() else { return "" }
        return "rifatcam://connect?ip=\(ip)&port=\(NetworkUtils.streamPort)&name=RifatCam%20iPhone"
    }

    struct QRConnectionData {
        let ip: String
        let port: Int
        let name: String
    }

    static func parseQRContent(_ content: String) -> QRConnectionData? {
        guard content.hasPrefix("rifatcam://connect?"),
              let components = URLComponents(string: content) else { return nil }
        let params = components.queryItems ?? []
        guard let ip = params.first(where: { $0.name == "ip" })?.value else { return nil }
        let port = Int(params.first(where: { $0.name == "port" })?.value ?? "") ?? Int(NetworkUtils.streamPort)
        let name = params.first(where: { $0.name == "name" })?.value ?? "RifatCam iPhone"
        return QRConnectionData(ip: ip, port: port, name: name)
    }
}

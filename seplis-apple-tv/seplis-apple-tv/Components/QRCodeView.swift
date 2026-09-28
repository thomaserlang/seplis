import CoreImage.CIFilterBuiltins
import SwiftUI

struct QRCodeView: View {
    private let image: CGImage?

    init(url: String) {
        let filter = CIFilter.qrCodeGenerator()
        filter.message = Data(url.utf8)
        filter.correctionLevel = "M"
        image = filter.outputImage.flatMap { CIContext().createCGImage($0, from: $0.extent) }
    }

    var body: some View {
        if let image {
            Image(decorative: image, scale: 1)
                .interpolation(.none)
                .resizable()
                .scaledToFit()
                .padding(24)
                .background(.white, in: RoundedRectangle(cornerRadius: 8))
                .accessibilityLabel("Authentication URL QR code")
        }
    }
}

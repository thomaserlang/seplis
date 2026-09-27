import AVFoundation

enum PlayerMetadata {
    static func items(title: String, subtitle: String?) -> [AVMetadataItem] {
        var values: [(AVMetadataIdentifier, String)] = [(.commonIdentifierTitle, title)]
        if let subtitle { values.append((.iTunesMetadataTrackSubTitle, subtitle)) }
        return values.map { identifier, value in
            let item = AVMutableMetadataItem()
            item.identifier = identifier
            item.value = value as NSString
            item.extendedLanguageTag = "und"
            return item
        }
    }
}

import UIKit

enum PlaybackInfoMenu {
    static func decision(_ decision: TranscodeDecision?, server: String?) -> UIMenu {
        var rows: [UIMenuElement] = [row("Delivery", "HLS stream")]
        if let decision {
            rows += [row("Video", decision.video.label), row("Audio", decision.audio.label)]
            rows += decision.reasons.map { row("Reason", $0) }
        } else {
            rows.append(row("Transcoding", "Not reported by the play server"))
        }
        if let server { rows.append(row("Server", server)) }
        let menu = UIMenu(title: "Playback Decision", children: rows)
        menu.subtitle = decision?.playbackMethod ?? "Unavailable"
        return menu
    }

    static func source(_ source: PlaySource, audioKey: String?) -> UIMenu {
        var rows: [UIMenuElement] = [row("Quality", source.resolution), row("Video codec", source.codec.uppercased())]
        if let width = source.width, let height = source.height {
            rows.append(row("Dimensions", "\(width) x \(height)"))
        }
        if let format = source.format { rows.append(row("Container", format.uppercased())) }
        if let range = source.videoColorRange { rows.append(row("Color range", range.uppercased())) }
        if let hdr = source.videoColorRangeType, !hdr.isEmpty { rows.append(row("HDR format", hdr.uppercased())) }
        if let fps = source.fps, fps > 0 {
            rows.append(row("Frame rate", "\(fps.formatted(.number.precision(.fractionLength(0...3)))) fps"))
        }
        if source.bitrate > 0 {
            rows.append(
                row(
                    "Bitrate",
                    "\((source.bitrate / 1_000_000).formatted(.number.precision(.fractionLength(0...2)))) Mbps"))
        }
        if let size = source.size, size > 0 {
            rows.append(
                row(
                    "File size",
                    "\((Double(size) / 1_000_000_000).formatted(.number.precision(.fractionLength(0...2)))) GB"))
        }
        if let audio = source.audio.first(where: { $0.key == audioKey }) {
            if let codec = audio.codec { rows.append(row("Audio codec", codec.uppercased())) }
            if let channels = audio.channels { rows.append(row("Audio channels", String(channels))) }
            rows.append(row("Audio language", audio.language))
        }
        return UIMenu(title: "Media Info", children: rows)
    }

    private static func row(_ title: String, _ value: String) -> UIAction {
        // Keep informational rows focusable so the remote can scroll the menu.
        let action = UIAction(title: title, attributes: .keepsMenuPresented) { _ in }
        action.subtitle = value
        return action
    }
}

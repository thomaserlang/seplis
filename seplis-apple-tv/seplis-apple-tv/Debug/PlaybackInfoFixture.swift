#if DEBUG
    import UIKit
    import SwiftUI

    struct PlaybackInfoFixture: UIViewControllerRepresentable {
        func makeUIViewController(context: Context) -> UIViewController {
            let controller = UIViewController()
            controller.view.backgroundColor = .black
            var audio = PlayStream(title: "English", language: "eng", groupIndex: 0, forced: false)
            audio.codec = "eac3"
            audio.channels = 6
            var source = PlaySource(
                index: 0, duration: 3600, bitrate: 25_000_000, codec: "hevc",
                resolution: "4K", audio: [audio], subtitles: [])
            source.width = 3840
            source.height = 2160
            source.format = "matroska"
            source.videoColorRange = "HDR"
            source.videoColorRangeType = "HDR10"
            source.fps = 23.976
            source.size = 11_250_000_000
            let decision = TranscodeDecision(
                method: "transcode", directPlay: .init(blockers: []),
                video: .init(action: "copy", sourceCodec: "hevc", targetCodec: "hevc", blockers: []),
                audio: .init(action: "transcode", sourceCodec: "eac3", targetCodec: "aac", blockers: []))
            let button = UIButton(type: .system)
            button.setTitle("Settings", for: .normal)
            button.menu = UIMenu(
                title: "Settings",
                children: [
                    PlaybackInfoMenu.decision(decision, server: "play.example.test"),
                    PlaybackInfoMenu.source(source, audioKey: audio.key),
                ])
            button.showsMenuAsPrimaryAction = true
            button.accessibilityIdentifier = "open-media-info"
            button.translatesAutoresizingMaskIntoConstraints = false
            controller.view.addSubview(button)
            NSLayoutConstraint.activate([
                button.centerXAnchor.constraint(equalTo: controller.view.centerXAnchor),
                button.centerYAnchor.constraint(equalTo: controller.view.centerYAnchor),
            ])
            return controller
        }

        func updateUIViewController(_ controller: UIViewController, context: Context) {}
    }
#endif

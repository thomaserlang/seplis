import AVKit
import SwiftUI

struct NativePlayerView: UIViewControllerRepresentable {
    let model: PlaybackModel
    let close: () -> Void
    let playNext: () -> Void

    func makeUIViewController(context: Context) -> AVPlayerViewController {
        let controller = AVPlayerViewController()
        controller.player = model.player
        controller.delegate = context.coordinator
        controller.showsPlaybackControls = true
        context.coordinator.controller = controller
        let back = UITapGestureRecognizer(target: context.coordinator, action: #selector(Coordinator.hideControls))
        back.allowedPressTypes = [NSNumber(value: UIPress.PressType.menu.rawValue)]
        back.delegate = context.coordinator
        controller.view.addGestureRecognizer(back)
        return controller
    }

    func updateUIViewController(_ controller: AVPlayerViewController, context: Context) {
        context.coordinator.close = close
        if controller.player !== model.player { controller.player = model.player }
        let sourceBitrate = model.candidates.indices.contains(model.selectedSource)
            ? model.candidates[model.selectedSource].source.bitrate : nil
        var menus: [UIMenuElement] = []
        var mediaMenus: [UIMenuElement] = []
        if model.candidates.indices.contains(model.selectedSource) {
            let sources = model.candidates.enumerated().map { index, candidate in
                UIAction(title: "\(index + 1). \(candidate.label)",
                         state: index == model.selectedSource ? .on : .off) { _ in model.selectSource(index) }
            }
            let sourceMenu = UIMenu(title: "Source", options: .singleSelection, children: sources)
            sourceMenu.subtitle = model.candidates[model.selectedSource].label
            mediaMenus.append(sourceMenu)
        }
        if model.candidates.indices.contains(model.selectedSource) {
            let streams = model.candidates[model.selectedSource].source.audio
            if streams.count > 1 {
                let audio = streams.map { stream in
                    UIAction(title: stream.displayTitle,
                             state: stream.key == model.audioKey ? .on : .off) { _ in model.selectAudio(stream.key) }
                }
                let audioMenu = UIMenu(title: "Audio", options: .singleSelection, children: audio)
                audioMenu.subtitle = streams.first { $0.key == model.audioKey }?.displayTitle
                menus.append(audioMenu)
            }
        }
        let quality = PlaybackQuality.options.filter {
            $0 == PlaybackQuality.maximum || $0 == model.preferences.maxBitrate
                || (model.candidates.indices.contains(model.selectedSource)
                    && Double($0) < model.candidates[model.selectedSource].source.bitrate)
        }.map { bitrate in
            UIAction(title: PlaybackQuality.label(bitrate, sourceBitrate: sourceBitrate), state: bitrate == model.preferences.maxBitrate ? .on : .off) { _ in
                model.selectBitrate(bitrate)
            }
        }
        let qualityMenu = UIMenu(title: "Quality", options: .singleSelection, children: quality)
        qualityMenu.subtitle = PlaybackQuality.label(model.preferences.maxBitrate, sourceBitrate: sourceBitrate)
        mediaMenus.append(qualityMenu)
        let hdr = UIAction(title: "HDR", attributes: model.isLoading ? .disabled : [],
                           state: model.preferences.hdrEnabled ? .on : .off) { _ in
            model.setHDR(!model.preferences.hdrEnabled)
        }
        hdr.subtitle = model.preferences.hdrEnabled ? "On" : "Off"
        let transcode = UIAction(title: "Force Transcode", attributes: model.isLoading ? .disabled : [],
                                 state: model.forceTranscode ? .on : .off) { _ in
            model.setForceTranscode(!model.forceTranscode)
        }
        transcode.subtitle = model.forceTranscode ? "On" : "Off"
        menus.insert(contentsOf: [hdr, transcode], at: 0)
        if !model.isLoading, model.error == nil, model.candidates.indices.contains(model.selectedSource) {
            let candidate = model.candidates[model.selectedSource]
            menus.insert(PlaybackInfoMenu.decision(model.playbackDecision, server: candidate.request.playUrl.host), at: 0)
            mediaMenus.append(PlaybackInfoMenu.source(candidate.source, audioKey: model.audioKey))
        }
        var controls: [UIMenuElement] = []
        if model.nextEpisode != nil {
            controls.append(UIAction(title: "Next Episode", image: UIImage(systemName: "forward.end.fill")) { _ in playNext() })
        }
        controls.append(UIMenu(title: "Settings", image: UIImage(systemName: "gearshape"), children: mediaMenus + menus))
        controller.transportBarCustomMenuItems = controls
        controller.contextualActions = []
    }

    func makeCoordinator() -> Coordinator { Coordinator(close: close) }

    final class Coordinator: NSObject, AVPlayerViewControllerDelegate, UIGestureRecognizerDelegate {
        var close: () -> Void
        weak var controller: AVPlayerViewController?
        private var controlsVisible = false
        init(close: @escaping () -> Void) { self.close = close }

        func gestureRecognizer(_ gestureRecognizer: UIGestureRecognizer, shouldReceive press: UIPress) -> Bool {
            controlsVisible && controller?.player?.timeControlStatus == .playing
                && controller?.presentedViewController == nil
        }

        @objc func hideControls() {
            // Hide the current controls while allowing AVKit to show them again on interaction.
            controller?.showsPlaybackControls = false
            controller?.showsPlaybackControls = true
        }

        func playerViewControllerShouldDismiss(_ playerViewController: AVPlayerViewController) -> Bool {
            close()
            return false
        }

        func playerViewController(_ playerViewController: AVPlayerViewController,
                                  willTransitionToVisibilityOfTransportBar visible: Bool,
                                  with coordinator: any AVPlayerViewControllerAnimationCoordinator) {
            controlsVisible = visible
        }
    }
}

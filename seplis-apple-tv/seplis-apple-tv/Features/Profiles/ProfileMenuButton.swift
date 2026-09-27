import SwiftUI
import UIKit

struct ProfileMenuButton: UIViewRepresentable {
    let accountName: String
    let menu: UIMenu
    let focusChanged: (Bool) -> Void
    let presentationChanged: (Bool) -> Void

    func makeUIView(context: Context) -> FocusMenuButton {
        let button = FocusMenuButton(type: .system)
        var configuration = UIButton.Configuration.plain()
        configuration.image = UIImage(systemName: "person.crop.circle")
        configuration.preferredSymbolConfigurationForImage = .init(pointSize: 26, weight: .semibold)
        configuration.imagePadding = 12
        configuration.titleLineBreakMode = .byTruncatingTail
        configuration.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { attributes in
            var attributes = attributes
            attributes.font = .systemFont(ofSize: 26, weight: .semibold)
            return attributes
        }
        button.configuration = configuration
        button.contentHorizontalAlignment = .leading
        button.accessibilityIdentifier = "profiles-menu"
        button.showsMenuAsPrimaryAction = true
        updateUIView(button, context: context)
        return button
    }

    func updateUIView(_ button: FocusMenuButton, context: Context) {
        button.configuration?.title = accountName
        button.accessibilityLabel = "Profiles, \(accountName)"
        button.menu = menu
        button.focusChanged = focusChanged
        button.presentationChanged = presentationChanged
    }
}

final class FocusMenuButton: UIButton {
    var focusChanged: ((Bool) -> Void)?
    var presentationChanged: ((Bool) -> Void)?
    private var menuVisible = false

    override func didUpdateFocus(in context: UIFocusUpdateContext, with coordinator: UIFocusAnimationCoordinator) {
        super.didUpdateFocus(in: context, with: coordinator)
        focusChanged?(isFocused)
        // Directional entry opens the menu; focus restoration after dismissal does not.
        guard context.nextFocusedView === self, !context.focusHeading.isEmpty, !menuVisible else { return }
        coordinator.addCoordinatedAnimations(nil) { [weak self] in
            guard let self, self.isFocused else { return }
            self.performPrimaryAction()
        }
    }

    override func contextMenuInteraction(_ interaction: UIContextMenuInteraction,
                                        willDisplayMenuFor configuration: UIContextMenuConfiguration,
                                        animator: (any UIContextMenuInteractionAnimating)?) {
        super.contextMenuInteraction(interaction, willDisplayMenuFor: configuration, animator: animator)
        menuVisible = true
        presentationChanged?(true)
    }

    override func contextMenuInteraction(_ interaction: UIContextMenuInteraction,
                                        willEndFor configuration: UIContextMenuConfiguration,
                                        animator: (any UIContextMenuInteractionAnimating)?) {
        super.contextMenuInteraction(interaction, willEndFor: configuration, animator: animator)
        let finished = { [weak self] in
            self?.menuVisible = false
            self?.presentationChanged?(false)
        }
        if let animator { animator.addCompletion(finished) } else { finished() }
    }
}

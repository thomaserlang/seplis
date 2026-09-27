import SwiftUI
import UIKit

struct AccountMenuTrigger: UIViewRepresentable {
    let accountName: String
    let focusChanged: (Bool) -> Void
    let open: () -> Void
    @Environment(\.isEnabled) private var isEnabled

    func makeUIView(context: Context) -> AccountTriggerControl {
        let button = AccountTriggerControl()
        button.accessibilityIdentifier = "profiles-menu"
        updateUIView(button, context: context)
        return button
    }

    func updateUIView(_ button: AccountTriggerControl, context: Context) {
        button.isEnabled = isEnabled
        button.nameLabel.text = accountName
        button.accessibilityLabel = "Profiles, \(accountName)"
        button.focusChanged = focusChanged
        button.open = open
    }
}

final class AccountTriggerControl: UIControl {
    let nameLabel = UILabel()
    var focusChanged: ((Bool) -> Void)?
    var open: (() -> Void)?

    override var canBecomeFocused: Bool { isEnabled }

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true
        accessibilityTraits = .button
        let icon = UIImageView(image: UIImage(systemName: "person.crop.circle",
                                             withConfiguration: UIImage.SymbolConfiguration(pointSize: 26, weight: .semibold)))
        icon.tintColor = .white
        icon.setContentHuggingPriority(.required, for: .horizontal)
        nameLabel.font = .systemFont(ofSize: 26, weight: .semibold)
        nameLabel.textColor = .white
        nameLabel.lineBreakMode = .byTruncatingTail
        let row = UIStackView(arrangedSubviews: [icon, nameLabel])
        row.spacing = 12
        row.alignment = .center
        row.isUserInteractionEnabled = false
        row.translatesAutoresizingMaskIntoConstraints = false
        addSubview(row)
        NSLayoutConstraint.activate([
            row.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 24),
            row.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -24),
            row.centerYAnchor.constraint(equalTo: centerYAnchor),
        ])
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    override func pressesEnded(_ presses: Set<UIPress>, with event: UIPressesEvent?) {
        guard presses.contains(where: { $0.type == .select }) else {
            super.pressesEnded(presses, with: event)
            return
        }
        open?()
    }

    override func accessibilityActivate() -> Bool {
        open?()
        return true
    }

    override func didUpdateFocus(in context: UIFocusUpdateContext, with coordinator: UIFocusAnimationCoordinator) {
        super.didUpdateFocus(in: context, with: coordinator)
        focusChanged?(isFocused)
        // Automatic launch/restoration focus must not open the account panel.
        if isFocused, !context.focusHeading.isEmpty { open?() }
    }
}

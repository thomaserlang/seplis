import { ArrowLeftIcon } from '@phosphor-icons/react'
import { Controls } from '@videojs/react'

interface PlayerHeaderProps {
    onClose?: () => void
    title?: string
    secondaryTitle?: string
}

export function PlayerHeader({
    onClose,
    title,
    secondaryTitle,
}: PlayerHeaderProps) {
    return (
        <Controls.Root className="media-header">
            {onClose && (
                <button
                    type="button"
                    className="media-button media-button--subtle media-button--icon media-header__close"
                    onClick={onClose}
                    aria-label="Close player"
                >
                    <ArrowLeftIcon className="media-icon" weight="bold" />
                </button>
            )}
            {title && (
                <div className="media-header__info">
                    <span className="media-header__title">{title}</span>
                    {secondaryTitle && (
                        <span className="media-header__secondaryTitle">
                            {secondaryTitle}
                        </span>
                    )}
                </div>
            )}
        </Controls.Root>
    )
}

import { ArrowLeftIcon } from '@phosphor-icons/react'
import { Controls } from '@videojs/react'
import { useEffect, useRef } from 'react'

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
    const ref = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const el = ref.current
        if (!el) return
        const stop = (e: PointerEvent) => e.stopPropagation()
        el.addEventListener('pointerdown', stop)
        el.addEventListener('pointerup', stop)
        return () => {
            el.removeEventListener('pointerdown', stop)
            el.removeEventListener('pointerup', stop)
        }
    }, [])

    return (
        <Controls.Root ref={ref} className="media-header">
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

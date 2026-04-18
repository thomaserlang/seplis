import { PageLoader } from '@/components/page-loader'
import { BufferingIndicator, ErrorDialog } from '@videojs/react'
import { PlayerError } from '../player-error'
import type { PlayerVideoStatusProps } from '../player-video.types'

export function PlayerVideoStatus({
    isPlayerLoading,
    error,
    hasData,
    isLoading,
    onClose,
}: PlayerVideoStatusProps) {
    return (
        <>
            <BufferingIndicator
                render={() => (
                    <div className="media-buffering-indicator">
                        <PageLoader />
                    </div>
                )}
            />

            {isPlayerLoading && <BlockingLoader />}

            <PlayerVideoErrorDialog onClose={onClose} />

            {error && (
                <PlayerError
                    title="Something went wrong on the play server"
                    errorObj={error}
                />
            )}

            {!hasData && !isLoading && !error && (
                <PlayerError title="No playable source found" />
            )}
        </>
    )
}

function BlockingLoader() {
    return (
        <div className="media-buffering-indicator" data-visible="">
            <PageLoader />
        </div>
    )
}

function PlayerVideoErrorDialog({ onClose }: { onClose?: () => void }) {
    return (
        <ErrorDialog.Root>
            <ErrorDialog.Popup className="media-error">
                <div className="media-error__dialog media-surface">
                    <div className="media-error__content">
                        <ErrorDialog.Title className="media-error__title">
                            Something went wrong.
                        </ErrorDialog.Title>
                        <ErrorDialog.Description className="media-error__description" />
                    </div>
                    <div className="media-error__actions">
                        {onClose && (
                            <ErrorDialog.Close
                                className="media-button media-button--subtle"
                                onClick={onClose}
                            >
                                Go Back
                            </ErrorDialog.Close>
                        )}
                        <ErrorDialog.Close
                            className="media-button media-button--primary"
                            onClick={() => window.location.reload()}
                        >
                            Refresh
                        </ErrorDialog.Close>
                    </div>
                </div>
            </ErrorDialog.Popup>
        </ErrorDialog.Root>
    )
}

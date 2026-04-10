import { MinusIcon, PlusIcon } from '@phosphor-icons/react'
import { type ReactNode } from 'react'
import classes from './player-settings.module.css'
import { SettingsBody } from './settings-body'
import { SubMenuHeader } from './sub-menu-header'

export function SubtitleSyncPanel({
    subtitleOffset,
    onSubtitleOffsetChange,
    back,
}: {
    subtitleOffset: number
    onSubtitleOffsetChange: (offset: number) => void
    back: () => void
}): ReactNode {
    return (
        <>
            <SubMenuHeader title="Subtitle Sync" onBack={back} />
            <SettingsBody>
                <div className={classes.sync}>
                    <div
                        role="button"
                        tabIndex={0}
                        className={classes.syncBtn}
                        onClick={() =>
                            onSubtitleOffsetChange(
                                Math.round((subtitleOffset - 0.5) * 10) / 10,
                            )
                        }
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault()
                                onSubtitleOffsetChange(
                                    Math.round((subtitleOffset - 0.5) * 10) /
                                        10,
                                )
                            }
                        }}
                    >
                        <MinusIcon weight="bold" />
                    </div>
                    <span className={classes.syncValue}>
                        {subtitleOffset === 0
                            ? '0s'
                            : `${subtitleOffset > 0 ? '+' : ''}${subtitleOffset.toFixed(1)}s`}
                    </span>
                    <div
                        role="button"
                        tabIndex={0}
                        className={classes.syncBtn}
                        onClick={() =>
                            onSubtitleOffsetChange(
                                Math.round((subtitleOffset + 0.5) * 10) / 10,
                            )
                        }
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault()
                                onSubtitleOffsetChange(
                                    Math.round((subtitleOffset + 0.5) * 10) /
                                        10,
                                )
                            }
                        }}
                    >
                        <PlusIcon weight="bold" />
                    </div>
                </div>
                <div
                    role="button"
                    tabIndex={subtitleOffset === 0 ? -1 : 0}
                    aria-disabled={subtitleOffset === 0}
                    className={classes.syncReset}
                    onClick={
                        subtitleOffset === 0
                            ? undefined
                            : () => onSubtitleOffsetChange(0)
                    }
                    onKeyDown={
                        subtitleOffset === 0
                            ? undefined
                            : (e) => {
                                  if (e.key === 'Enter' || e.key === ' ') {
                                      e.preventDefault()
                                      onSubtitleOffsetChange(0)
                                  }
                              }
                    }
                >
                    Reset
                </div>
            </SettingsBody>
        </>
    )
}

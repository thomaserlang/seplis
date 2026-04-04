import { ActionIcon, Button, Group, Popover } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { MinusIcon, PlusIcon } from '@phosphor-icons/react'
import classes from './watched-button.module.css'

interface Props {
    times?: number
    position?: number
    runtime?: number | null
    loading?: boolean
    onIncrement?: () => void
    onDecrement?: () => void
}

export function WatchedButton({
    onIncrement,
    onDecrement,
    times = 0,
    position = 0,
    runtime,
    loading = false,
}: Props) {
    const [opened, { toggle, close }] = useDisclosure(false)

    const handleMainClick = times === 0 && position === 0 ? onIncrement : toggle

    const progressClass =
        position > 0
            ? times > 0
                ? classes.inProgressCompleted
                : classes.inProgress
            : times > 0
              ? classes.watched
              : classes.notWatched

    const progressPercent = Math.max(
        0,
        Math.min(100, runtime ? (position / (runtime * 60)) * 100 : 50),
    )

    return (
        <>
            <Popover position="top" opened={opened} onChange={close}>
                <Popover.Target>
                    <Button.Group>
                        <Button
                            variant="filled"
                            size="compact-md"
                            className={progressClass}
                            onClick={handleMainClick}
                            loading={loading}
                            style={
                                position > 0
                                    ? ({
                                          '--progress': `${progressPercent}%`,
                                      } as React.CSSProperties)
                                    : undefined
                            }
                        >
                            Watched
                        </Button>
                        <Button
                            variant="outline"
                            size="compact-md"
                            className={classes.timesWatched}
                            onClick={handleMainClick}
                            loading={loading}
                            title={`${times} time${times !== 1 ? 's' : ''} watched`}
                        >
                            {times}
                        </Button>
                    </Button.Group>
                </Popover.Target>
                <Popover.Dropdown p="xs">
                    <Group gap="xs">
                        <ActionIcon
                            color="red"
                            aria-label="Decrement watched"
                            onClick={() => {
                                close()
                                onDecrement?.()
                            }}
                            loading={loading}
                        >
                            <MinusIcon />
                        </ActionIcon>
                        <ActionIcon
                            color="teal"
                            aria-label="Increment watched"
                            onClick={() => {
                                onIncrement?.()
                                close()
                            }}
                            loading={loading}
                        >
                            <PlusIcon />
                        </ActionIcon>
                    </Group>
                </Popover.Dropdown>
            </Popover>
        </>
    )
}

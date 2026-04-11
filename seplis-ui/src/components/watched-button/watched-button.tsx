import {
    ActionIcon,
    Button,
    ButtonSize,
    Group,
    MantineStyleProp,
    Popover,
} from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { CheckIcon, MinusIcon, PlusIcon } from '@phosphor-icons/react'
import classes from './watched-button.module.css'

interface Props {
    times?: number
    position?: number
    duration?: number | null
    loading?: boolean
    size?: ButtonSize
    onIncrement?: () => void
    onDecrement?: () => void
}

export function WatchedButton({
    onIncrement,
    onDecrement,
    times = 0,
    position = 0,
    duration,
    loading = false,
    size = 'compact-md',
}: Props) {
    const [opened, { toggle, close }] = useDisclosure(false)

    const handleMainClick = times === 0 && position === 0 ? onIncrement : toggle

    const progressPercent =
        position > 0
            ? Math.max(
                  15,
                  Math.min(
                      100,
                      duration ? (position / (duration * 60)) * 100 : 50,
                  ),
              )
            : 0

    const style: MantineStyleProp = {}

    style['--watched'] = 'oklch(0.4 0.07 240)'
    style['--progress-color'] = 'oklch(0.55 0.1 240)'

    if (position > 0) {
        style['--progress'] = `${progressPercent}%`
    }

    if (times > 0) {
        style['--button-bg'] = 'var(--watched)'
        style['--button-hover'] =
            'color-mix(in oklab, var(--watched) 95%, white)'
        style['--button-active'] = 'var(--watched)'
    }

    return (
        <>
            <Popover position="top" opened={opened} onChange={close}>
                <Popover.Target>
                    <Button.Group>
                        <Button
                            leftSection={
                                <CheckIcon
                                    weight={times > 0 ? 'fill' : 'regular'}
                                />
                            }
                            variant="default"
                            size={size}
                            className={classes.progress}
                            onClick={handleMainClick}
                            loading={loading}
                            style={style}
                        >
                            Watched
                        </Button>
                        <Button
                            variant="default"
                            size={size}
                            onClick={handleMainClick}
                            loading={loading}
                            title={`${times} time${times !== 1 ? 's' : ''} watched`}
                            className={classes.times}
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

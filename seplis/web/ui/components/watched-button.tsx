import { AddIcon, MinusIcon } from "@chakra-ui/icons"
import { Box, Button, ButtonGroup, IconButton, Popover, PopoverContent, PopoverTrigger, Stack, useDisclosure } from "@chakra-ui/react"
import { forwardRef } from "react"

interface IProps {
    times?: number
    position?: number
    isUpdating?: boolean
    onIncrement: () => void
    onDecrement: () => void
}

export default function WatchedButton({ onIncrement, onDecrement, times = 0, position = 0, isUpdating = false }: IProps) {
    const { onOpen, onClose, isOpen } = useDisclosure()

    return <Box>
        <Popover
            isOpen={isOpen}
            onClose={onClose}
            placement='top'
            closeOnBlur={true}
            variant="responsive"
        >
            <PopoverTrigger>
                <BaseButton
                    times={times}
                    position={position}
                    onClick={times == 0 ? onIncrement : onOpen}
                    isUpdating={isUpdating}
                />
            </PopoverTrigger>
            <PopoverContent padding="0.5rem">
                <Stack direction="row">
                    <IconButton
                        colorScheme="red"
                        aria-label="Decrement watched"
                        icon={<MinusIcon />}
                        onClick={() => {
                            onClose()
                            onDecrement()
                        }}
                        isLoading={isUpdating}
                    />
                    <IconButton
                        colorScheme="green"
                        aria-label="Increment watched"
                        icon={<AddIcon />}
                        onClick={() => {
                            onIncrement()
                            onClose()
                        }}
                        isLoading={isUpdating}
                    />
                </Stack>
            </PopoverContent>
        </Popover>
    </Box>
}

interface IButton {
    times: number
    position: number
    onClick?: () => void
    isUpdating: boolean
}

const BaseButton = forwardRef<any, IButton>((props, ref) => {
    return <ButtonGroup ref={ref} isAttached variant='outline'>
        <Button
            colorScheme={props.times > 0 ? "green" : null}
            variant={props.times > 0 ? "solid" : 'outline'}
            style={props.position > 0 ? {
                background: "linear-gradient(90deg, #428bca 56%, var(--chakra-colors-green-300) 44%)"
            } : null}
            onClick={props.onClick}
            isLoading={props.isUpdating}
        >
            Watched
        </Button>
        <Button onClick={props.onClick}>{props.times}</Button>
    </ButtonGroup>
})
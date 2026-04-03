import { Anchor, Image } from '@mantine/core'
import { Link } from 'react-router-dom'

interface Props {
    size?: string
    hideShadow?: boolean
}

export function Logo({ size = '4rem', hideShadow = false }: Props) {
    return (
        <Anchor component={Link} to="/">
            <Image
                radius="50%"
                w={size}
                h={size}
                src="/img/android-chrome-96x96.png"
                style={{
                    boxShadow: hideShadow
                        ? 'none'
                        : `0 0 calc(${size} * 0.5) calc(${size} * 0.15) rgba(66, 133, 244, 0.4)`,
                }}
            />
        </Anchor>
    )
}

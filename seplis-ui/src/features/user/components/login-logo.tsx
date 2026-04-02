import { Anchor, Image } from '@mantine/core'
import { Link } from 'react-router-dom'

export function LoginLogo() {
    return (
        <Anchor component={Link} to="/">
            <Image
                radius="50%"
                w="4rem"
                src="/img/android-chrome-96x96.png"
                style={{ boxShadow: '0 0 20px 6px rgba(66, 133, 244, 0.4)' }}
            />
        </Anchor>
    )
}

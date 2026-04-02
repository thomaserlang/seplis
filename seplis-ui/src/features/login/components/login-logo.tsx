import { Anchor, Image } from '@mantine/core'
import { Link } from 'react-router-dom'

export function LoginLogo() {
    return (
        <Anchor component={Link} to="/">
            <Image radius="50%" w="4rem" src="/img/android-chrome-96x96.png" />
        </Anchor>
    )
}

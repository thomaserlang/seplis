import { Box} from '@chakra-ui/react'
import { CastButton, useCast } from './react-cast-sender'

export default function ChromecastIcon() {
    const { initialized } = useCast()
    return initialized && <Box width="24px" height="24px" mr="1.25rem">
        <CastButton />
    </Box>
}
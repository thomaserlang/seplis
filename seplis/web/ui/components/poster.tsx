import { Center, Image, Text } from "@chakra-ui/react"

interface IProps {
    url: string
    title: string
}

export function Poster({ url, title }: IProps) {
    return <Image
        src={url}
        fallback={<Center height='100%' backgroundColor="blackAlpha.400"><Text>
            {title || 'No title'}
        </Text></Center>}
    />
}
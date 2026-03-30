import { AspectRatio, Center, Image, Text } from "@chakra-ui/react"

interface IProps {
    url: string | null | undefined
    title: string | null | undefined
    onClick?: () => void
}

export function Poster({ url, title, onClick }: IProps) {
    return <Image
        onClick={onClick}
        src={url ?? undefined}
        fallback={<Center height='100%' backgroundColor="blackAlpha.400"><Text>
            {title || 'No title'}
        </Text></Center>}
    />
}


export function PosterAspectRatio({ url, title, onClick }: IProps) {
    return <AspectRatio
        height="100%"
        width="100%"
        ratio={603 / 887}
        onClick={onClick}
        cursor={onClick ? 'pointer' : 'auto'}
    >
        <Image
            src={url ?? undefined}
            fallback={<Center height='100%' backgroundColor="blackAlpha.400"><Text>
                {title || 'No title'}
            </Text></Center>}
            objectFit="cover"
        />
    </AspectRatio>
}
import { ErrorBox } from '@/components/error-box'
import { Container, Flex, Text } from '@mantine/core'

interface Props {
    title: string
    errorObj?: Error | string | unknown
}

export function PlayerError({ title, errorObj }: Props) {
    return (
        <Container
            h="100%"
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
            }}
        >
            <Flex gap="2rem" direction="column">
                <Flex gap="1rem" direction="column">
                    <Text size="xl" fw={600}>
                        {title}
                    </Text>
                    <ErrorBox errorObj={errorObj} />
                </Flex>
            </Flex>
        </Container>
    )
}

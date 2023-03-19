import { Avatar, Box, Button, Flex, Heading, Text } from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'

export default function FullErrorPage({ message }: { message: string }) {
    const navigate = useNavigate()
    return <Flex h="100vh" py={10} px={5} alignItems="center">
        <Box maxW="xl" mx="auto" textAlign="center">
            
            <Flex justifyContent="center" mb={5}>
                <Avatar src="/static/img/apple-touch-icon.png" />
            </Flex>
            
            <Heading size="4xl" mb={5}>
                Sorry!
            </Heading>
            <Text fontSize="xl" mb={10}>
                {message}
            </Text>
            <Text fontSize="lg" mb={3}>
                Please try again later.
            </Text>
            <Flex gap="1rem" justifyContent="center">
                <Button size="lg" onClick={() => {
                    navigate(-1)
                }}>Go Back</Button>
                <Button size="lg" onClick={() => {
                    navigate(0)
                }}>Refresh</Button>
            </Flex>
        </Box>
    </Flex>
}
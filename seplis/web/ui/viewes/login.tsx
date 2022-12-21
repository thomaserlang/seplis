import {
  Flex,
  Heading,
  Input,
  Button,
  InputGroup,
  Stack,
  InputLeftElement,
  chakra,
  Box,
  Link,
  Avatar,
  FormControl,
  FormHelperText,
} from '@chakra-ui/react'
import { FaUserAlt, FaLock } from 'react-icons/fa'
import { useForm } from 'react-hook-form'

const CFaUserAlt = chakra(FaUserAlt);
const CFaLock = chakra(FaLock);

export default function Login() {
    const {
        handleSubmit,
        register,
        formState: { errors, isSubmitting },
    } = useForm()

    const onSubmit = handleSubmit((data) => {
        console.log(data)
    })

    return <Flex
        flexDirection="column"
        width="100wh"
        justifyContent="center"
        alignItems="center"
        marginTop="2rem"
    >
        <Stack
            flexDir="column"
            mb="2"
            justifyContent="center"
            alignItems="center"
            spacing="1rem"
        >
            <Avatar src="/static/img/apple-touch-icon.png" />
            <Box minW={{ base: "90%", md: "468px" }} p="2rem" backgroundColor="blackAlpha.300" rounded="md">
                <form onSubmit={onSubmit}>
                <Stack spacing="1rem">
                    <Heading>Log in to SEPLIS</Heading>
                    <FormControl>
                        <InputGroup>
                            <InputLeftElement pointerEvents="none" children={<CFaUserAlt />} />
                            <Input {...register('login')} type="input" placeholder="email or username" isRequired />
                        </InputGroup>
                    </FormControl>
                    <FormControl>
                        <InputGroup>
                            <InputLeftElement pointerEvents="none" children={<CFaLock />} />
                            <Input {...register('password')} type="password" placeholder="Password" isRequired/>
                        </InputGroup>
                        <FormHelperText textAlign="right">
                            <Link>Reset password</Link>
                        </FormHelperText>
                    </FormControl>
                    <Stack alignItems="end">
                        <Button type="submit" colorScheme="blue">Log in</Button>
                    </Stack>
                </Stack>
                </form>
            </Box>
            <Box>
                <Link href="#">
                    Sign up
                </Link>
            </Box>
        </Stack>
    </Flex>
}
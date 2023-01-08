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
  Alert,
  AlertTitle,
  AlertIcon,
} from '@chakra-ui/react'
import { FaUserAlt, FaLock } from 'react-icons/fa'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { StringParam, useQueryParam } from 'use-query-params'
import { IToken } from '@seplis/interfaces/token'
import { ErrorMessageFromResponse } from '@seplis/components/error'

const CFaUserAlt = chakra(FaUserAlt)
const CFaLock = chakra(FaLock)

interface ILogin {
    login: string
    password: string
    next: string
}

export default function Login() {
    const { handleSubmit, register, formState: { isSubmitting }, resetField, setFocus, setValue } = useForm<ILogin>()
    const [ error, setError ] = useState<string>(null)
    const [ next ] = useQueryParam('next', StringParam)
    const navigate = useNavigate()
    useEffect(() => {
        document.title = 'Login in | SEPLIS'
        setValue('next', next)
    }, [])

    const onSubmit = handleSubmit(async (data) => {
        try {
            setError(null)
            const r = await axios.post<IToken>('/api/token', {
                login: data.login,
                password: data.password,
            })
            localStorage.setItem('accessToken', r.data.access_token)
            navigate(data.next?data.next:'/')
        } catch(e) {
            setError(ErrorMessageFromResponse(e))
            resetField('password')
            setFocus('password')
        }
    })

    return <Flex
        flexDirection="column"
        width="100wh"
        justifyContent="center"
        alignItems="center"
        marginTop="4rem"
    >
        <Stack
            flexDir="column"
            mb="2"
            justifyContent="center"
            alignItems="center"
            spacing="1rem"
        >
            <Avatar src="/static/img/apple-touch-icon.png" />
            <Box minW={{ base: "90%", md: "468px" }} p="2rem" backgroundColor="blackAlpha.400" rounded="md">
                <form onSubmit={onSubmit}>
                <Stack spacing="1rem">
                    <Heading>Log in to SEPLIS</Heading>

                    {error && <Alert status="error" rounded="md">
                        <AlertIcon />
                        <AlertTitle>{error}</AlertTitle>    
                    </Alert>}

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
                    
                    <Input {...register('next')} type="hidden" />
                        
                    <Stack align="end">
                        <div>
                            <Button type="submit" colorScheme="blue" isLoading={isSubmitting} loadingText='Logging in'>Log in</Button>
                        </div>
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
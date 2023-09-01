import { Flex, Heading, Input, Button, InputGroup, Stack, InputLeftElement, Box, Avatar, FormControl, FormErrorMessage, Alert, AlertIcon, AlertTitle } from '@chakra-ui/react'
import { FaUserAlt, FaLock, FaEnvelope } from 'react-icons/fa'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { IToken } from '@seplis/interfaces/token'
import { setAuthorizationHeader } from '@seplis/api'
import { setTitle } from '@seplis/utils'
import { IError, IValidationError } from '@seplis/interfaces/error'


interface ISignUp {
    [key: string]: string
    username: string
    password: string
    email: string
}

export default function Login() {
    const { handleSubmit, register, formState: { isSubmitting, errors }, setFocus, setError } = useForm<ISignUp>()
    const [rootError, setRootError] = useState<string>()
    const navigate = useNavigate()

    useEffect(() => {
        setTitle('Sign up')
        setFocus('username')
    }, [location.pathname])

    const submit = async (data: ISignUp) => {
        try {
            setRootError(null)
            const r = await axios.post<IToken>('/api/signup', data)
            localStorage.setItem('accessToken', r.data.access_token)
            setAuthorizationHeader()
            navigate('/')
        } catch (e) {
            const data = e.response.data as IError<IValidationError>

            if (data?.errors) {
                for (const e of data?.errors) {
                    setError(e.field[1], { message: e.message })
                }
            } else {
                if (data.code == 1501)
                    setError('email', {message: data.message})
                else if (data.code == 1502)
                    setError('username', {message: data.message})
                else
                    setRootError(data.message)
            }
        }
    }
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
                <form
                    onSubmit={handleSubmit(submit)}
                    onKeyDown={(event) => {
                        if (event.key === "Enter")
                            handleSubmit(submit)()
                    }}
                >
                    <Stack spacing="1rem">
                        <Heading>Sign up to SEPLIS</Heading>

                        {rootError && <Alert status="error" rounded="md">
                            <AlertIcon />
                            {rootError}
                        </Alert>}

                        <FormControl isInvalid={errors?.username !== undefined}>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaUserAlt />} />
                                <Input id="username" {...register('username')} type="input" placeholder="Username" />
                            </InputGroup>
                            <FormErrorMessage>
                                {errors.username?.message}
                            </FormErrorMessage>
                        </FormControl>

                        <FormControl isInvalid={errors?.email !== undefined}>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaEnvelope />} />
                                <Input id="email" {...register('email')} type="input" placeholder="Email" />
                            </InputGroup>
                            <FormErrorMessage>
                                {errors.email?.message}
                            </FormErrorMessage>
                        </FormControl>

                        <FormControl isInvalid={errors?.password !== undefined}>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaLock />} />
                                <Input id="password" {...register('password')} type="password" placeholder="Password" />
                            </InputGroup>
                            <FormErrorMessage>
                                {errors.password?.message}
                            </FormErrorMessage>
                        </FormControl>

                        <Flex>
                            <Button
                                marginLeft="auto"
                                type="submit"
                                colorScheme="blue"
                                isLoading={isSubmitting}
                                loadingText='Creating user'
                                paddingLeft="2rem"
                                paddingRight="2rem">
                                Sign up
                            </Button>
                        </Flex>
                    </Stack>
                </form>
            </Box>
            <Box>
                <Link to="/login">
                    Login
                </Link>
            </Box>
        </Stack>
    </Flex>
}
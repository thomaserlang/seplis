import { Flex, Heading, Input, Button, InputGroup, Stack, InputLeftElement, Box, Avatar, FormControl, FormHelperText, Alert, AlertTitle, AlertIcon } from '@chakra-ui/react'
import { FaUserAlt, FaLock } from 'react-icons/fa'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { StringParam, useQueryParam } from 'use-query-params'
import { IToken } from '@seplis/interfaces/token'
import { ErrorMessageFromResponse } from '@seplis/components/error'
import api, { setAuthorizationHeader } from '@seplis/api'
import { IUser, IUsersLoggedIn } from '@seplis/interfaces/user'


interface ILogin {
    login: string
    password: string
    next: string
}

export default function Login() {
    const { handleSubmit, register, formState: { isSubmitting }, resetField, setFocus, setValue } = useForm<ILogin>()
    const [error, setError] = useState<JSX.Element>(null)
    const [next] = useQueryParam('next', StringParam)
    const navigate = useNavigate()

    useEffect(() => {
        document.title = 'Log in | SEPLIS'
        setValue('next', next)
        setFocus('login')
    }, [])

    const submit = async (data: ILogin) => {
        try {
            setError(null)
            const r = await axios.post<IToken>('/api/token', {
                login: data.login,
                password: data.password,
            })
            localStorage.setItem('accessToken', r.data.access_token)
            setAuthorizationHeader()
            const user = await api.get<IUser>('/2/users/me')
            const users: IUsersLoggedIn = JSON.parse(localStorage.getItem('users')) || {}
            users[user.data.id] = {
                ...user.data,
                token: r.data.access_token
            }
            localStorage.setItem('users', JSON.stringify(users))
            localStorage.setItem('activeUser', JSON.stringify(user.data))

            navigate(data.next ? data.next : '/')
        } catch (e) {
            setError(ErrorMessageFromResponse(e))
            resetField('password')
            setFocus('password')
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
                        <Heading>Log in to SEPLIS</Heading>

                        {error && <Alert status="error" rounded="md">
                            <AlertIcon />
                            {error}
                        </Alert>}

                        <FormControl>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaUserAlt />} />
                                <Input {...register('login', { required: true })} type="input" placeholder="Email or username" />
                            </InputGroup>
                        </FormControl>

                        <FormControl>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaLock />} />
                                <Input {...register('password', { required: true })} type="password" placeholder="Password" />
                            </InputGroup>
                            <FormHelperText textAlign="right">
                                <Link to="/users/reset-password">Reset password</Link>
                            </FormHelperText>
                        </FormControl>

                        <Input {...register('next')} type="hidden" />

                        <Flex>
                            <Button
                                marginLeft="auto"
                                type="submit"
                                colorScheme="blue"
                                isLoading={isSubmitting}
                                loadingText='Logging in'
                                paddingLeft="2rem"
                                paddingRight="2rem">
                                Login
                            </Button>
                        </Flex>
                    </Stack>
                </form>
            </Box>
            <Box>
                <Link to="/signup">
                    Sign up
                </Link>
            </Box>
        </Stack>
    </Flex>
}
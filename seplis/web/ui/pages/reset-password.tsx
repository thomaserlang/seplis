import { Flex, Heading, Input, Button, InputGroup, Stack, InputLeftElement, Box, Avatar, FormControl, FormErrorMessage, Alert, AlertIcon, AlertTitle } from '@chakra-ui/react'
import { FaEnvelope, FaLock } from 'react-icons/fa'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { IToken } from '@seplis/interfaces/token'
import { setTitle } from '@seplis/utils'
import { IError, IValidationError } from '@seplis/interfaces/error'
import { ErrorMessageFromResponse } from '@seplis/components/error'


interface INewPassword {
    [key: string]: string
    new_password: string
    key: string
}

export default function ResetPassword() {
    const { handleSubmit, register, formState: { isSubmitting, errors }, setFocus, setError } = useForm<INewPassword>()
    const [rootError, setRootError] = useState<JSX.Element>()
    const navigate = useNavigate()
    const { key } = useParams()

    useEffect(() => {
        setTitle('Reset password')
        setFocus('new_password')
    }, [])

    const submit = async (data: INewPassword) => {
        try {
            setRootError(null)
            await axios.post<IToken>('/api/reset-password', data)
            navigate('/login')
        } catch (e) {
            const data = e.response.data as IError<IValidationError>
            if (data?.errors) {
                for (const e of data?.errors) {
                    setError(e.field[1], { message: e.message })
                }
            } else {
                setRootError(ErrorMessageFromResponse(e))
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
                        <Heading>New password to SEPLIS</Heading>

                        {rootError && <Alert status="error" rounded="md">
                            <AlertIcon />
                            {rootError}
                        </Alert>}

                        <FormControl isInvalid={!!errors?.new_password}>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaLock />} />
                                <Input {...register('new_password', { required: true })} type="password" placeholder="New password" />
                            </InputGroup>
                            <FormErrorMessage>
                                {errors.new_password?.message}
                            </FormErrorMessage>
                        </FormControl>
                        <input {...register('key')} value={key} type="hidden" />

                        <Flex>
                            <Button
                                marginLeft="auto"
                                type="submit"
                                colorScheme="blue"
                                isLoading={isSubmitting}
                                loadingText='Changing password'
                                paddingLeft="2rem"
                                paddingRight="2rem">
                                Change password
                            </Button>
                        </Flex>
                    </Stack>
                </form>
            </Box>
            <Flex gap="1rem">
                <Link to="/login">Login</Link>
                <Link to="/signup">Sign up</Link>
            </Flex>
        </Stack>
    </Flex>
}
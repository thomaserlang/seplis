import { Flex, Heading, Input, Button, InputGroup, Stack, InputLeftElement, Box, Avatar, FormControl, FormErrorMessage, Alert, AlertIcon, AlertTitle } from '@chakra-ui/react'
import { FaEnvelope } from 'react-icons/fa'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { setTitle } from '@seplis/utils'
import { IError, IValidationError } from '@seplis/interfaces/error'


interface IResetPassword {
    [key: string]: string
    email: string
}

export default function SendResetPassword() {
    const { handleSubmit, register, formState: { isSubmitting, errors }, setFocus, setError } = useForm<IResetPassword>()
    const [rootError, setRootError] = useState<string>()
    const [success, setSuccess] = useState<string>()

    useEffect(() => {
        setTitle('Reset password')
        setFocus('email')
    }, [location.pathname])

    const submit = async (data: IResetPassword) => {
        try {
            setRootError(null)
            await axios.post('/api/send-reset-password', data)
            setSuccess('A password reset link has been sent to your email.')
        } catch (e) {
            const data = e.response.data as IError<IValidationError>

            if (data?.errors) {
                for (const e of data?.errors) {
                    setError(e.field[1], { message: e.message })
                }
            } else {
                setRootError('Failed to send password reset link, please try again')
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
                        <Heading>Reset password to SEPLIS</Heading>

                        {rootError && <Alert status="error" rounded="md">
                            <AlertIcon />
                            {rootError}
                        </Alert>}

                        <FormControl isInvalid={errors?.email !== undefined}>
                            <InputGroup>
                                <InputLeftElement pointerEvents="none" children={<FaEnvelope />} />
                                <Input {...register('email', { disabled: !!success, required: true })} type="input" placeholder="Email" />
                            </InputGroup>
                            <FormErrorMessage>
                                {errors.email?.message}
                            </FormErrorMessage>
                        </FormControl>

                        {success && <Alert status="success" rounded="md">
                            <AlertIcon />
                            {success}
                        </Alert>}

                        {!success && <Flex>
                            <Button
                                marginLeft="auto"
                                type="submit"
                                colorScheme="blue"
                                isLoading={isSubmitting}
                                loadingText='Sending reset password link'
                                paddingLeft="2rem"
                                paddingRight="2rem">
                                Reset password
                            </Button>
                        </Flex>}
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
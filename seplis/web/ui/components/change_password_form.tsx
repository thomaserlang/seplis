import { Flex, Heading, Input, Button, Stack, Box, FormControl, Alert, AlertIcon, FormLabel, FormErrorMessage } from '@chakra-ui/react'
import { useForm } from 'react-hook-form'
import { useEffect, useState } from 'react'
import { ErrorMessageFromResponse } from '@seplis/components/error'
import api from '@seplis/api'
import { IError, IValidationError } from '@seplis/interfaces/error'


interface IChangePassword {
    [key: string]: any
    current_password: string
    new_password: string
}

export default function ChangePasswordForm() {
    const { handleSubmit, register, formState: { isSubmitting, errors, isSubmitSuccessful }, setError, setFocus } = useForm<IChangePassword>()
    const [rootError, setRootError] = useState<JSX.Element>()

    useEffect(() => {
        setFocus('current_password')
    }, [])

    const submit = async (data: IChangePassword) => {
        try {
            setRootError(null)
            await api.post<IChangePassword>('/2/users/me/change-password', data)
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

    if (!rootError && isSubmitSuccessful)
        return <Alert status="success" rounded="md">
            <AlertIcon /> Your password has been changed.
        </Alert>

    return <form
        onSubmit={handleSubmit(submit)}
        onKeyDown={(event) => {
            if (event.key === "Enter")
                handleSubmit(submit)()
        }}
    >
        <Stack spacing="1rem">
            {rootError && <Alert status="error" rounded="md">
                <AlertIcon /> {rootError}
            </Alert>}

            <FormControl isInvalid={!!errors?.current_password}>
                <FormLabel>Current password</FormLabel>
                <Input {...register('current_password', { required: true })} type="password" />
                <FormErrorMessage>
                    {errors.current_password?.message}
                </FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors?.new_password}>
                <FormLabel>New password</FormLabel>
                <Input {...register('new_password', { required: true })} type="password" />
                <FormErrorMessage>
                    {errors.new_password?.message}
                </FormErrorMessage>
            </FormControl>

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
}
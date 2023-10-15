import { Alert, AlertDialog, AlertDialogBody, AlertDialogContent, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, Box, Button, Flex, FormControl, FormLabel, Heading, Input, Stack, useDisclosure, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovie } from '@seplis/interfaces/movie'
import { TExternals } from '@seplis/interfaces/types'
import { useQueryClient } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { ErrorMessageFromResponse } from '../error'
import { IError } from '@seplis/interfaces/error'


export function MovieNew({ onDone }: { onDone?: (seriesId: number) => void }) {
    const onSave = async (data: IData) => {
        const result = await api.post<IMovie>('/2/movies', data)
        if (onDone)
            onDone(result.data.id)
        return result.data
    }

    return <SettingsForm
        externals={{}}
        onSave={onSave}
    />
}

export function MovieUpdate({ movie }: { movie: IMovie }) {
    const onSave = async (data: IData) => {
        const result = await api.patch<IMovie>(`/2/movies/${movie.id}`, data)
        api.post(`/2/movies/${movie.id}/update`)
        return result.data
    }

    return <SettingsForm
        movieId={movie.id}
        externals={movie.externals}
        onSave={onSave}
    />
}


interface IData {
    externals: TExternals
    onSave: (data: IData) => Promise<IMovie>
    movieId?: number
}

export default function SettingsForm({ externals, onSave, movieId }: IData) {
    const { handleSubmit, register, formState: { isSubmitting } } = useForm<IData>({
        defaultValues: {
            externals: { ...externals }
        }
    })
    const [error, setError] = useState<JSX.Element>(null)
    const toast = useToast()
    const queryClient = useQueryClient()

    const onSubmit = handleSubmit(async (data) => {
        try {
            setError(null)
            const movie = await onSave(data)
            toast({
                title: 'Movie saved',
                status: 'success',
                isClosable: true,
                position: 'top',
            })
            queryClient.setQueryData(['movie', movie.id], movie)
        } catch (e) {
            setError(ErrorMessageFromResponse(e))
        }
    })

    return <Box>
        <form onSubmit={onSubmit}>
            <Stack spacing="1rem">
                {error && <Alert status="error" rounded="md">
                    {error}
                </Alert>}

                <Heading fontSize="1.25rem">Externals</Heading>
                <FormControl>
                    <FormLabel>IMDb</FormLabel>
                    <Input {...register('externals.imdb')} type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TMDb</FormLabel>
                    <Input {...register('externals.themoviedb')} type='text' />
                </FormControl>

                <Flex align="end" justifyContent="end" gap="1rem" basis="100%">
                    {movieId && <DeleteConfirm movieId={movieId} />}
                    <Button type="submit" colorScheme="blue" isLoading={isSubmitting} loadingText='Saving'>Save</Button>
                </Flex>
            </Stack>
        </form>
    </Box>
}


function DeleteConfirm({ movieId }: { movieId: number }) {
    const { isOpen, onOpen, onClose } = useDisclosure()
    const cancelRef = useRef()
    const toast = useToast()

    const onDelete = async () => {
        try {
            await api.delete(`/2/movies/${movieId}`)
            location.reload()
            toast({
                title: 'Movie deleted',
                status: 'success',
                duration: 5000,
                isClosable: true,
                position: 'top',
            })
        } catch (e) {
            toast({
                title: 'Failed to delete the movie',
                description: (e.response.data as IError).message,
                status: 'error',
                duration: 9000,
                isClosable: true,
                position: 'top',
            })
        }
        onClose()
    }

    return <>
        <Button colorScheme='red' onClick={onOpen}>
            Delete
        </Button>

        <AlertDialog
            isOpen={isOpen}
            leastDestructiveRef={cancelRef}
            onClose={onClose}
            isCentered
        >
            <AlertDialogOverlay>
                <AlertDialogContent>
                    <AlertDialogHeader fontSize='lg' fontWeight='bold'>
                        Delete Movie
                    </AlertDialogHeader>

                    <AlertDialogBody>
                        Are you sure? You can't undo this action afterwards.
                    </AlertDialogBody>

                    <AlertDialogFooter>
                        <Button ref={cancelRef} onClick={onClose}>
                            Cancel
                        </Button>
                        <Button colorScheme='red' onClick={onDelete} ml={3}>
                            Delete
                        </Button>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialogOverlay>
        </AlertDialog>
    </>
}
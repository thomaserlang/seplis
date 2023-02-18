import { Alert, Box, Button, FormControl, FormLabel, Heading, Input, Stack, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovie } from '@seplis/interfaces/movie'
import { TExternals } from '@seplis/interfaces/types'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ErrorMessageFromResponse } from '../error'


export function MovieNew({onDone}: {onDone?: (seriesId: number) => void}) {
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
        externals={movie.externals}
        onSave={onSave}
    />
}


interface IData {
    externals: TExternals
    onSave: (data: IData) => Promise<IMovie>
}

export default function SettingsForm({ externals, onSave }: IData) {    
    const { handleSubmit, register, formState: { isSubmitting } } = useForm<IData>({
        defaultValues: {
            externals: {...externals}
        }
    })
    const [ error, setError ] = useState<JSX.Element>(null)
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
            queryClient.setQueryData(['movies', movie.id], movie)
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
                    <Input {...register('externals.imdb')}  type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TMDb</FormLabel>
                    <Input {...register('externals.themoviedb')}  type='text' />
                </FormControl>

                <Stack align="end">
                    <Button type="submit" colorScheme="blue" isLoading={isSubmitting} loadingText='Saving'>Save</Button>
                </Stack>
            </Stack>
        </form>
    </Box>
}
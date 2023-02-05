import { Alert, AlertIcon, AlertTitle, Box, Button, FormControl, FormLabel, Heading, Input, Stack, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { ISeries } from '@seplis/interfaces/series'
import { TExternals } from '@seplis/interfaces/types'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ErrorMessageFromResponse } from '../error'

interface IData {
    externals: TExternals
}

export default function Settings({ series }: { series: ISeries }) {    
    const { handleSubmit, register, formState: { isSubmitting } } = useForm<IData>({
        defaultValues: {
            externals: {...series.externals}
        }
    })
    const [ error, setError ] = useState<string>(null)
    const toast = useToast()

    const onSubmit = handleSubmit(async (data) => {
        try {
            setError(null)
            await api.patch<ISeries>(`/2/series/${series.id}`, data)
            toast({
                title: 'Series settings saved',
                status: 'success',
                isClosable: true,
                position: 'top',
            })
            api.post(`/2/series/${series.id}/update`)
        } catch(e) {
            setError(ErrorMessageFromResponse(e))
        }
    })

    return <Box>
        <form onSubmit={onSubmit}>
            <Stack spacing="1rem">
                {error && <Alert status="error" rounded="md">
                    <AlertIcon />
                    <AlertTitle>{error}</AlertTitle>    
                </Alert>}

                <Heading fontSize="1.25rem">Externals</Heading>                        
                <FormControl>
                    <FormLabel>IMDb</FormLabel>
                    <Input {...register('externals.imdb')}  type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>The Movie DB</FormLabel>
                    <Input {...register('externals.themoviedb')}  type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TVMaze</FormLabel>
                    <Input {...register('externals.tvmaze')}  type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TheTVDB</FormLabel>
                    <Input {...register('externals.thetvdb', {})}  type='text' />
                </FormControl>

                <Stack align="end">
                    <Button type="submit" colorScheme="blue" isLoading={isSubmitting} loadingText='Saving'>Save</Button>
                </Stack>
            </Stack>
        </form>
    </Box>
}
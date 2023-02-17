import { Alert, AlertIcon, AlertTitle, Button, Flex, FormControl, FormLabel, Heading, Input, Select, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { ISeries, ISeriesImporters } from '@seplis/interfaces/series'
import { TExternals } from '@seplis/interfaces/types'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ErrorMessageFromResponse } from '../error'

interface IData {
    externals: TExternals
    importers: ISeriesImporters
}

export default function Settings({ series }: { series: ISeries }) {
    const { handleSubmit, register, formState: { isSubmitting } } = useForm<IData>({
        defaultValues: {
            externals: { ...series.externals },
            importers: { ...series.importers },
        }
    })
    const [error, setError] = useState<JSX.Element>(null)
    const toast = useToast()
    const queryClient = useQueryClient()

    const onSubmit = handleSubmit(async (data) => {
        try {
            setError(null)
            const result = await api.patch<ISeries>(`/2/series/${series.id}`, data)
            toast({
                title: 'Series settings saved',
                status: 'success',
                isClosable: true,
                position: 'top',
            })
            queryClient.setQueryData(['series', series.id], result.data)
            api.post(`/2/series/${series.id}/update`)
        } catch (e) {
            setError(ErrorMessageFromResponse(e))
        }
    })

    return <form onSubmit={onSubmit}>
        <Flex wrap="wrap" gap="1rem">
            {error && <Alert status="error" rounded="md">
                <AlertIcon />
                <AlertTitle>{error}</AlertTitle>
            </Alert>}

            <Flex direction="column" gap="0.5rem" basis="400px">
                <Heading fontSize="1.25rem" fontWeight="600">Externals</Heading>
                <FormControl>
                    <FormLabel>IMDb</FormLabel>
                    <Input {...register('externals.imdb')} type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>The Movie DB</FormLabel>
                    <Input {...register('externals.themoviedb')} type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TVMaze</FormLabel>
                    <Input {...register('externals.tvmaze')} type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TheTVDB</FormLabel>
                    <Input {...register('externals.thetvdb', {})} type='text' />
                </FormControl>
            </Flex>

            <Flex direction="column" gap="0.5rem" basis="400px">
                <Heading fontSize="1.25rem" fontWeight="600">Importers</Heading>
                <FormControl>
                    <FormLabel>Info</FormLabel>
                    <Select {...register('importers.info')}>
                        <option value="themoviedb">The Movie DB</option>
                        <option value="thetvdb">TheTVDB</option>
                        <option value="tvmaze">TVMaze</option>
                    </Select>
                </FormControl>

                <FormControl>
                    <FormLabel>Episodes</FormLabel>
                    <Select {...register('importers.episodes')}>
                        <option value="themoviedb">The Movie DB</option>
                        <option value="thetvdb">TheTVDB</option>
                        <option value="tvmaze">TVMaze</option>
                    </Select>
                </FormControl>
            </Flex>

            <Flex align="end" justifyContent="end" gap="1rem" basis="100%">
                <Button type="submit" colorScheme="blue" isLoading={isSubmitting} loadingText='Saving'>Save</Button>
            </Flex>
        </Flex>
    </form>
}
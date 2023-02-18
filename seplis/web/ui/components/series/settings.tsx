import { Alert, Button, Flex, FormControl, FormLabel, Heading, Input, Select, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { ISeries, ISeriesImporters } from '@seplis/interfaces/series'
import { TExternals } from '@seplis/interfaces/types'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ErrorMessageFromResponse } from '../error'


export function SeriesNew({onDone}: {onDone?: (seriesId: number) => void}) {
    const onSave = async (data: IData) => {
        const result = await api.post<ISeries>('/2/series', data)
        if (onDone)
            onDone(result.data.id)
        return result.data
    }

    return <SettingsForm
        externals={{}}
        importers={{info: '', episodes: ''}}
        onSave={onSave}
    />
}


export function SeriesUpdate({ series }: { series: ISeries }) {
    const onSave = async (data: IData) => {
        const result = await api.patch<ISeries>(`/2/series/${series.id}`, data)
        api.post(`/2/series/${series.id}/update`)
        return result.data
    }

    return <SettingsForm
        externals={series.externals}
        importers={series.importers}
        onSave={onSave}
    />
}


interface IData {
    externals: TExternals
    importers: ISeriesImporters
    onSave: (data: IData) => Promise<ISeries>
}

export function SettingsForm({ externals, importers, onSave }: IData) {
    const { handleSubmit, register, formState: { isSubmitting } } = useForm<IData>({
        defaultValues: {
            externals: { ...externals },
            importers: { ...importers },
        }
    })
    const [error, setError] = useState<JSX.Element>(null)
    const toast = useToast()
    const queryClient = useQueryClient()

    const onSubmit = handleSubmit(async (data) => {
        try {
            setError(null)
            const series = await onSave(data)
            toast({
                title: 'Series saved',
                status: 'success',
                isClosable: true,
                position: 'top',
            })
            queryClient.setQueryData(['series', series.id], series)
        } catch (e) {
            setError(ErrorMessageFromResponse(e))
        }
    })

    return <form onSubmit={onSubmit}>
        <Flex wrap="wrap" gap="1rem">
            {error && <Alert status="error" rounded="md">
                {error}
            </Alert>}

            <Flex direction="column" gap="0.5rem" basis="400px">
                <Heading fontSize="1.25rem" fontWeight="600">Externals</Heading>
                <FormControl>
                    <FormLabel>IMDb</FormLabel>
                    <Input {...register('externals.imdb', {required: true})} type='text' />
                </FormControl>

                <FormControl>
                    <FormLabel>TMDb</FormLabel>
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
                        <option value="themoviedb">TMDb</option>
                        <option value="thetvdb">TheTVDB</option>
                        <option value="tvmaze">TVMaze</option>
                    </Select>
                </FormControl>

                <FormControl>
                    <FormLabel>Episodes</FormLabel>
                    <Select {...register('importers.episodes')}>
                        <option value="themoviedb">TMDb</option>
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
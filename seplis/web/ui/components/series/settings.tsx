import { Alert, AlertDialog, AlertDialogBody, AlertDialogContent, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, Button, Flex, FormControl, FormLabel, Heading, Input, Select, useDisclosure, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { ISeries, ISeriesRequest } from '@seplis/interfaces/series'
import { useQueryClient } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { useForm, UseFormRegister } from 'react-hook-form'
import { ErrorMessageFromResponse } from '../error'
import { IError } from '@seplis/interfaces/error'


export function SeriesNew({ onDone }: { onDone?: (seriesId: number) => void }) {
    const onSave = async (data: ISeriesRequest) => {
        const result = await api.post<ISeries>('/2/series', data)
        if (onDone)
            onDone(result.data.id)
        return result.data
    }

    return <SeriesForm
        request={{
            externals: {},
            importers: { info: '', episodes: '' },
            episode_type: 2,
        }}
        onSave={onSave}
    />
}


export function SeriesUpdate({ series }: { series: ISeries }) {
    const onSave = async (data: ISeriesRequest) => {
        const result = await api.patch<ISeries>(`/2/series/${series.id}`, data)
        api.post(`/2/series/${series.id}/update`)
        return result.data
    }

    return <SeriesForm
        seriesId={series.id}
        request={{
            externals: { ...series.externals },
            importers: { ...series.importers },
            episode_type: series.episode_type,
        }}
        onSave={onSave}
    />
}

export function SeriesForm({ request, onSave, onDelete, seriesId }: { request: ISeriesRequest, onSave: (request: ISeriesRequest) => Promise<ISeries>, onDelete?: () => void, seriesId?: number }) {
    const { handleSubmit, register, formState: { isSubmitting } } = useForm<ISeriesRequest>({
        defaultValues: { ...request }
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

            <Flex wrap="wrap" gap="1rem">
                <Flex direction="column" gap="1rem" grow="1">
                    <Heading fontSize="1.25rem" fontWeight="600">Externals</Heading>
                    <Externals register={register} />
                </Flex>

                <Flex direction="column" gap="0.5rem" grow="1">
                    <Heading fontSize="1.25rem" fontWeight="600">Importers</Heading>
                    <Importers register={register} />
                </Flex>

                <Flex direction="column" gap="0.5rem" grow="1">
                    <Heading fontSize="1.25rem" fontWeight="600">Extra</Heading>
                    <EpisodeType register={register} />
                </Flex>
            </Flex>


            <Flex align="end" justifyContent="end" gap="1rem" basis="100%">
                {seriesId && <DeleteConfirm seriesId={seriesId} />}
                <Button type="submit" colorScheme="blue" isLoading={isSubmitting} loadingText='Saving'>Save</Button>
            </Flex>
        </Flex>
    </form >
}


function Importers({ register }: { register: UseFormRegister<ISeriesRequest> }) {
    return <Flex gap="0.5rem" wrap="wrap">
        <Flex grow="1">
            <FormControl>
                <FormLabel>Info</FormLabel>
                <Select {...register('importers.info')}>
                    <option value="themoviedb">TMDb</option>
                    <option value="thetvdb">TheTVDB</option>
                    <option value="tvmaze">TVMaze</option>
                </Select>
            </FormControl>
        </Flex>

        <Flex grow="1">
            <FormControl>
                <FormLabel>Episodes</FormLabel>
                <Select {...register('importers.episodes')}>
                    <option value="themoviedb">TMDb</option>
                    <option value="thetvdb">TheTVDB</option>
                    <option value="tvmaze">TVMaze</option>
                </Select>
            </FormControl>
        </Flex>
    </Flex>
}


function Externals({ register }: { register: UseFormRegister<ISeriesRequest> }) {
    return <Flex gap="0.5rem" grow="1" wrap="wrap">
        <FormControl>
            <FormLabel>IMDb</FormLabel>
            <Input {...register('externals.imdb', { required: true })} type='text' />
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
            <Input {...register('externals.thetvdb')} type='text' />
        </FormControl>
    </Flex>
}


function EpisodeType({ register }: { register: UseFormRegister<ISeriesRequest> }) {
    return <Flex gap="0.5rem" grow="1" direction="column">
        <FormControl>
            <FormLabel>Episode type</FormLabel>
            <Select {...register('episode_type')}>
                <option value={1}>Absolute number</option>
                <option value={2}>Season episode</option>
                <option value={3}>Air date</option>
            </Select>
        </FormControl>
    </Flex>
}

function DeleteConfirm({ seriesId }: { seriesId: number }) {
    const { isOpen, onOpen, onClose } = useDisclosure()
    const cancelRef = useRef()
    const toast = useToast()

    const onDelete = async () => {
        try {
            await api.delete(`/2/series/${seriesId}`)
            //location.href = '/'
        } catch (e) {
            toast({
                title: 'Failed to delete series',
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
                        Delete Series
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
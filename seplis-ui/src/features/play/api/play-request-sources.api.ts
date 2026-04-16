import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import ky from 'ky'
import { PlayRequest } from '../types/play-request.types'
import {
    PlayRequestSources,
    PlaySource,
} from '../types/play-source.types'

interface PlayRequestSourcesGetProps extends ApiHelperProps<{}> {
    playRequests: PlayRequest[]
}

export const { get: getPlayRequestSources, useGet: useGetPlayRequestSources } =
    useApiHelper<PlayRequestSources[], PlayRequestSourcesGetProps>({
        url: () => '',
        queryKey: ({ playRequests }) => [
            'play-request-sources',
            ...playRequests.map((pr) => pr.play_id),
        ],
        getFn: async ({ playRequests, signal }) => {
            const data = await Promise.all(
                playRequests.map((playRequest) =>
                    getPlayServerSources(playRequest, signal),
                ),
            )
            return data.filter(
                (item): item is PlayRequestSources => item !== null,
            )
        },
    })

export async function getPlayServerSources(
    playRequest: PlayRequest,
    signal?: AbortSignal,
): Promise<PlayRequestSources | null> {
    try {
        const result = await ky.get<PlaySource[]>(
            playRequest.play_url + '/sources',
            {
                searchParams: {
                    play_id: playRequest.play_id,
                },
                timeout: 2000,
                signal,
            },
        )
        const data: PlayRequestSources = {
            request: playRequest,
            sources: await result.json(),
        }
        return data
    } catch (e) {
        if (e instanceof DOMException && e.name === 'AbortError') return null
        console.log(e)
        return null
    }
}

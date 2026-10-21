import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import ky from 'ky'
import { PlayRequest } from '../types/play-request.types'
import { PlayRequestSources, PlaySource } from '../types/play-source.types'

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
            signal?.throwIfAborted()
            if (!playRequests.length) return []

            const controller = new AbortController()
            let timer: ReturnType<typeof setTimeout> | undefined
            let onAbort: (() => void) | undefined
            try {
                return await new Promise<PlayRequestSources[]>(
                    (resolve, reject) => {
                        const results: PlayRequestSources[] = []
                        let gracePeriodElapsed = false
                        const finish = () => resolve(results.filter(Boolean))
                        onAbort = () => reject(signal?.reason)
                        signal?.addEventListener('abort', onAbort, {
                            once: true,
                        })
                        timer = setTimeout(() => {
                            gracePeriodElapsed = true
                            if (results.length) finish()
                        }, 2000)
                        void Promise.all(
                            playRequests.map(async (playRequest, index) => {
                                const result = await getPlayServerSources(
                                    playRequest,
                                    controller.signal,
                                )
                                if (result?.sources.length) {
                                    results[index] = result
                                    if (gracePeriodElapsed) finish()
                                }
                            }),
                        ).then(finish, reject)
                    },
                )
            } finally {
                clearTimeout(timer)
                if (onAbort) signal?.removeEventListener('abort', onAbort)
                controller.abort()
            }
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
                timeout: 20000,
                signal,
            },
        )
        const data: PlayRequestSources = {
            request: playRequest,
            sources: await result.json(),
        }
        return data
    } catch (e) {
        if (signal?.aborted) return null
        if (e instanceof DOMException && e.name === 'AbortError') return null
        console.log(e)
        return null
    }
}

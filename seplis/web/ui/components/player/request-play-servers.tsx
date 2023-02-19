import api from '@seplis/api'
import { IPlayRequest, IPlayServerSources, IPlaySource } from '@seplis/interfaces/play-server'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'


export function useGetPlayServers(url: string) {
    return useQuery(['play-server', url], async () => {
        const result = await api.get<IPlayRequest[]>(url)

        const sourcePromises: Promise<IPlayServerSources>[] = []
        for (const request of result.data) {
            sourcePromises.push(getPlayServerSources(request))
        }
        const sources = await Promise.all(sourcePromises)
        return sources.filter(item => item !== null)
    })
}


async function getPlayServerSources(playRequest: IPlayRequest) {
    try {
        const result = await axios.get<IPlaySource[]>(playRequest.play_url + '/sources', {
            params: {
                'play_id': playRequest.play_id,
            },
            timeout: 2000,

        })
        const data: IPlayServerSources = {
            request: playRequest,
            sources: result.data,
        }
        return data
    } catch (e) {
        console.log(e)
        return null
    }
}
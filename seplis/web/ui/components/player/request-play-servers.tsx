import api from '@seplis/api'
import { IPlayRequest, IPlayServerRequestSources, IPlaySource } from '@seplis/interfaces/play-server'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'


export function useGetPlayServers(url: string) {
    return useQuery(['play-server', url], async () => {
        return await getPlayServers(url)
    })
}


export async function getPlayServers(url: string) {
    const result = await api.get<IPlayRequest[]>(url)
    const sourcePromises: Promise<IPlayServerRequestSources>[] = []
    for (const request of result.data) 
        sourcePromises.push(getPlayServerSources(request))
    const requestSources = await Promise.all(sourcePromises)
    return requestSources.filter(item => item !== null)
} 


async function getPlayServerSources(playRequest: IPlayRequest) {
    try {
        const result = await axios.get<IPlaySource[]>(playRequest.play_url + '/sources', {
            params: {
                'play_id': playRequest.play_id,
            },
            timeout: 2000,

        })
        const data: IPlayServerRequestSources = {
            request: playRequest,
            sources: result.data,
        }
        return data
    } catch (e) {
        console.log(e)
        return null
    }
}
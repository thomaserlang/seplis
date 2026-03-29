import Axios, { AxiosError, AxiosRequestConfig } from 'axios'
import { IPageCursorResult } from './interfaces/page'

export const apiBaseUrl =
    import.meta.env.VITE_API_URL || 'https://api.seplis.net'

const api = Axios.create({
    baseURL: apiBaseUrl,
    paramsSerializer: {
        indexes: null,
    },
})

export function setAuthorizationHeader() {
    if (localStorage.getItem('accessToken'))
        api.defaults.headers['Authorization'] =
            `Bearer ${localStorage.getItem('accessToken')}`
    else api.defaults.headers['Authorization'] = null
}

setAuthorizationHeader()

api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error?.response?.status == 401)
            location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`
        throw error
    },
)

export default api

export async function GetAllCursor<T = any, D = any>(
    url: string,
    config?: AxiosRequestConfig<D>,
) {
    if (!config) config = {}
    let result = await api.get<IPageCursorResult<T>>(url, config)
    if (!config.params) config.params = {}
    const items = result.data.items
    if (result.data.cursor)
        do {
            config.params['cursor'] = result.data.cursor
            result = await api.get<IPageCursorResult<T>>(url, config)
            items.push(...result.data.items)
        } while (result.data.cursor !== null)
    return items
}

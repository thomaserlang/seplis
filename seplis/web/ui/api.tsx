import Axios, { AxiosError } from 'axios'


const api = Axios.create({
    baseURL: (window as any).seplisAPI
})

export function setAuthorizationHeader() {
    if (localStorage.getItem('accessToken'))
        api.defaults.headers['Authorization'] = `Bearer ${localStorage.getItem('accessToken')}`
}

setAuthorizationHeader()

api.interceptors.response.use((response) => response, (error: AxiosError) => {
    if (error?.response?.status == 401) 
        location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`
    throw error
})

export default api

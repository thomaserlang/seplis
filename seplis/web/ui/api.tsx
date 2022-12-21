import Axios from 'axios'

const axios = Axios.create({
    baseURL: (window as any).seplisBaseUrl
})
if (localStorage.getItem('accessToken'))
    axios.defaults.headers['Authorization'] = localStorage.getItem('accessToken')

export default axios

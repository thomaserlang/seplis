import ky from 'ky'

const apiClient = ky.create({
    prefixUrl: '/api',
    hooks: {
        beforeRequest: [
            (request) => {
                const token = localStorage.getItem('accessToken')
                if (token) {
                    request.headers.set('Authorization', `Bearer ${token}`)
                } else {
                    request.headers.delete('Authorization')
                }
            },
        ],
        afterResponse: [
            (_request, _options, response) => {
                if (
                    response.status === 401 &&
                    !location.pathname.startsWith('/login')
                ) {
                    location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`
                }
            },
        ],
    },
})

export { apiClient }

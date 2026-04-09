import ky, { isHTTPError } from 'ky'

const apiClient = ky.create({
    prefix: '/api',
    retry: {
        limit: 3,
        jitter: true,
        shouldRetry: ({ error }) => {
            if (isHTTPError(error)) {
                return error.response.status >= 500
            }
        },
    },
    hooks: {
        beforeError: [
            async ({ error }) => {
                if (
                    isHTTPError(error) &&
                    error.response.headers
                        .get('content-type')
                        ?.includes('application/json')
                ) {
                    error.data = await error.response.clone().json()
                }
                return error
            },
        ],
        beforeRequest: [
            ({ request }) => {
                const token = localStorage.getItem('accessToken')
                if (token) {
                    request.headers.set('Authorization', `Bearer ${token}`)
                } else {
                    request.headers.delete('Authorization')
                }
            },
        ],
        afterResponse: [
            ({ response }) => {
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

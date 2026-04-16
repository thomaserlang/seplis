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
                if (isHTTPError(error)) {
                    try {
                        const response = error.response.clone()
                        const contentType =
                            response.headers.get('content-type') || ''

                        if (contentType.includes('application/json')) {
                            error.data = await response.json()
                        } else {
                            const text = await response.text()
                            if (text) error.data = text
                        }
                    } catch {
                        // Ignore secondary body-read errors and keep the original HTTP error.
                    }
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

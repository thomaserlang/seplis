import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { PlayServer } from '../types/play-server.types'

interface PlayServersGetProps extends ApiHelperProps<{}> {}

export const {
    getPage: getPlayServers,
    useGetPage: useGetPlayServers,
    queryKey: playServersQueryKey,
} = usePageApiHelper<PlayServer, PlayServersGetProps>({
    url: () => '/2/play-servers',
    queryKey: ({ params }) => ['play-servers', params].filter(Boolean),
})

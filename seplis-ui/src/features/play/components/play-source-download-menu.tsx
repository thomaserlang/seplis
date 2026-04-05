import { errorMessageFromResponse } from '@/components/error-box'
import {
    PlayRequest,
    PlayRequestSources,
    PlaySource,
} from '@/features/play/types/play-source.types'
import { Button, Menu, Text } from '@mantine/core'
import { CaretDownIcon } from '@phosphor-icons/react'
import prettyBytes from 'pretty-bytes'
import { useState } from 'react'
import { useGetPlayRequestSources } from '../api/play-server-sources.api'
import { playSourceStr } from '../utils/play-source.utils'

interface Props {
    playRequests: PlayRequest[]
}

export function PlaySourceDownloadMenu({ playRequests }: Props) {
    const [opened, setOpened] = useState(false)
    return (
        <Menu opened={opened} onChange={setOpened}>
            <Menu.Target>
                <Button size="compact-md" variant="default">
                    <CaretDownIcon />
                </Button>
            </Menu.Target>
            <Menu.Dropdown>
                {opened && <MenuItems playRequests={playRequests} />}
            </Menu.Dropdown>
        </Menu>
    )
}

function MenuItems({ playRequests }: { playRequests: PlayRequest[] }) {
    const { data, isLoading, isFetching, error } = useGetPlayRequestSources({
        playRequests,
    })

    if (isLoading || isFetching) return <Menu.Item>Loading...</Menu.Item>

    if (error) return <Menu.Item>{errorMessageFromResponse(error)}</Menu.Item>

    if (!data || data.length === 0)
        return <Menu.Item>No sources available</Menu.Item>

    return (
        <>
            <Menu.Label>Sources</Menu.Label>
            {data.map((playServer: PlayRequestSources) =>
                playServer.sources.map((source: PlaySource) => (
                    <Menu.Item
                        component="a"
                        href={`${playServer.request.play_url}/source?play_id=${playServer.request.play_id}&source_index=${source.index}`}
                        key={`${playServer.request.play_url}-${source.index}`}
                        target="_blank"
                    >
                        <Text size="sm">
                            Download ({playSourceStr(source)} -{' '}
                            {prettyBytes(source.size)})
                        </Text>
                    </Menu.Item>
                )),
            )}
        </>
    )
}

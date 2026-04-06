import { errorMessageFromResponse } from '@/components/error-box'
import {
    PlayRequest,
    PlayRequestSources,
    PlaySource,
} from '@/features/play/types/play-source.types'
import { Menu } from '@mantine/core'
import { DownloadIcon } from '@phosphor-icons/react'
import prettyBytes from 'pretty-bytes'
import { Fragment, useState } from 'react'
import { useGetPlayRequestSources } from '../api/play-request-sources.api'
import { playSourceStr } from '../utils/play-source.utils'

interface Props {
    children: React.ReactElement<{ onClick: () => void }>
    playRequests: PlayRequest[] | undefined
    getPlayRequests: () => void
}

export function PlaySourceDownloadMenu({
    children,
    playRequests,
    getPlayRequests,
}: Props) {
    const [opened, setOpened] = useState(false)
    return (
        <Menu
            opened={opened}
            onChange={(opened) => {
                setOpened(opened)
                getPlayRequests()
            }}
        >
            <Menu.Target>{children}</Menu.Target>
            <Menu.Dropdown>
                {playRequests && playRequests.length > 0 && opened && (
                    <MenuItems playRequests={playRequests} />
                )}
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

    // TODO display the name of the play server it comes from
    return data.map((playServer: PlayRequestSources) => (
        <Fragment key={playServer.request.play_id}>
            <Menu.Label>Download</Menu.Label>
            {playServer.sources.map((source: PlaySource) => (
                <Menu.Item
                    component="a"
                    href={`${playServer.request.play_url}/source?play_id=${playServer.request.play_id}&source_index=${source.index}`}
                    key={`${playServer.request.play_url}-${source.index}`}
                    target="_blank"
                    leftSection={<DownloadIcon weight="bold" />}
                >
                    {playSourceStr(source)} ({prettyBytes(source.size)})
                </Menu.Item>
            ))}
        </Fragment>
    ))
}

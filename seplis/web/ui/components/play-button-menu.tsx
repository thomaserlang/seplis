import { IconButton, Menu, MenuButton, MenuGroup, MenuItem, MenuList } from '@chakra-ui/react'
import { useGetPlayServers } from './player/request-play-servers'
import { ChevronDownIcon } from '@chakra-ui/icons'
import { renderPlaySource } from './player/pick-source'
import prettyBytes from 'pretty-bytes'

interface IProps {
    playServersUrl: string,
}

export function PlayButtonMenu({ playServersUrl }: IProps) {

    return <Menu isLazy>
        <MenuButton as={IconButton} icon={<ChevronDownIcon />} />
        <MenuList>
            {PlayButtonMenuItems({ playServersUrl })}
        </MenuList>
    </Menu>
}

function PlayButtonMenuItems({ playServersUrl }: { playServersUrl: string }) {   
    const playServers = useGetPlayServers(playServersUrl)

    if (playServers.isLoading || playServers.isFetching)
        return <MenuItem>Loading...</MenuItem>

    if (!playServers.data || (playServers.data.length === 0))
        return <MenuItem>Error loading play servers</MenuItem>

    return <MenuGroup title="Sources">
        {playServers.data.map(playServer => (playServer.sources.map(source => (
            <MenuItem 
                as='a'
                href={`${playServer.request.play_url}/source?play_id=${playServer.request.play_id}&source_index=${source.index}`}
                key={`${playServer.request.play_url}-${source.index}`}
                target='_blank'
            >
                Download ({renderPlaySource(source)} - {prettyBytes(source.size)})
            </MenuItem>
        ))))}
    </MenuGroup>
}
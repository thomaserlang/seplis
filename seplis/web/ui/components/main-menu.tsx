import { ChevronDownIcon } from '@chakra-ui/icons'
import { Avatar, Box, Button, Flex, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Stack } from '@chakra-ui/react'
import { Link, } from 'react-router-dom'
import { SearchButtonDialog } from './search'

export default function MainMenu() {
    return <Flex
        backgroundColor="blackAlpha.500"
        padding="0.6rem"
        paddingLeft="1rem"
        paddingRight="1rem"
        alignItems="center"
    >

        <Flex
            fontSize="2xl"
            color="seplis.100"
            fontWeight="600"
            marginRight="0.75rem"
        >
            SEPLIS
        </Flex>

        <Button marginRight="0.75rem">Watch</Button>

        <Menu>
            <MenuButton as={Button} rightIcon={<ChevronDownIcon />} marginRight="0.75rem">
                Series
            </MenuButton>
            <MenuList>
                <Link to="/series/home"><MenuItem>Home</MenuItem></Link>
                <Link to="/series/following"><MenuItem>Following</MenuItem></Link>
                <Link to="/series/watched"><MenuItem>Watched</MenuItem></Link>
                <MenuItem>Stats</MenuItem>
                <MenuDivider />
                <MenuItem>New series</MenuItem>
            </MenuList>
        </Menu>


        <Menu>
            <MenuButton as={Button} rightIcon={<ChevronDownIcon />} marginRight="0.75rem">
                Movies
            </MenuButton>
            <MenuList>
                <Link to="/movies/home"><MenuItem>Home</MenuItem></Link>
                <Link to="/movies/stared"><MenuItem>Stared</MenuItem></Link>
                <Link to="/movies/watched"><MenuItem>Watched</MenuItem></Link>
                <MenuDivider />
                <MenuItem>New movie</MenuItem>
            </MenuList>
        </Menu>

        <Box marginRight="0.75rem">
            <SearchButtonDialog />
        </Box>

        <Box
            style={{ marginLeft: 'auto' }}
        >
            <Avatar size="md" name='USER' />
        </Box>

    </Flex>
}
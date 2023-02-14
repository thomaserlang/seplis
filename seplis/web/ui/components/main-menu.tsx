import { ChevronDownIcon } from '@chakra-ui/icons'
import { Avatar, Box, Button, Flex, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Stack } from '@chakra-ui/react'
import { Link, useNavigate } from 'react-router-dom'
import { SearchButtonDialog } from './search'

export default function MainMenu() {
    const navigate = useNavigate()

    function click(url: string) {
        navigate(url)
    }

    return <Stack
        backgroundColor="blackAlpha.500"
        padding="0.6rem"
        paddingLeft="1rem"
        paddingRight="1rem"
        alignItems="center"
        direction="row"
        spacing="0.75rem"
    >

        <Flex
            fontSize="2xl"
            color="seplis.100"
            fontWeight="600"
        >
            SEPLIS
        </Flex>

        <Button>Watch</Button>

        <Menu>
            <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
                Series
            </MenuButton>
            <MenuList>
                <Link to="/series/home"><MenuItem>Home</MenuItem></Link>
                <MenuItem>Air dates</MenuItem>
                <MenuItem>Countdown</MenuItem>
                <MenuItem>Following</MenuItem>
                <MenuItem>Series to Watch</MenuItem>
                <MenuItem>Recently aired</MenuItem>
                <MenuItem>Watched</MenuItem>
                <MenuItem>Stats</MenuItem>
                <MenuDivider />
                <MenuItem>New series</MenuItem>
            </MenuList>
        </Menu>


        <Menu>
            <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
                Movies
            </MenuButton>
            <MenuList>
                <Link to="/movies/home"><MenuItem>Home</MenuItem></Link>
                <MenuItem>Stared</MenuItem>
                <MenuItem>Watched</MenuItem>
                <MenuDivider />
                <MenuItem>New movie</MenuItem>
            </MenuList>
        </Menu>

        <SearchButtonDialog />

        <Box
            style={{ marginLeft: 'auto' }}
        >
            <Avatar size="md" name='USER' />
        </Box>

    </Stack>
}
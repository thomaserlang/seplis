import { ChevronDownIcon, SearchIcon } from '@chakra-ui/icons'
import { Avatar, Box, Button, Flex, IconButton, Menu, MenuButton, MenuDivider, MenuItem, MenuList } from '@chakra-ui/react'
import { Link, useNavigate } from 'react-router-dom'
import { SearchButtonDialog } from './search'

export default function MainMenu() {
    const navigate = useNavigate()

    function click(url: string) {
        navigate(url)
    }

    return <Flex 
        gap="0.75rem"
        backgroundColor="blackAlpha.500"
        padding="0.6rem"
        paddingLeft="1rem"
        paddingRight="1rem"
        justifyContent="center" 
        alignItems="center"
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
                <MenuItem>Episodes to Watch</MenuItem>
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
                <MenuItem>Stared</MenuItem>
                <MenuItem>Watched</MenuItem>
                <MenuDivider />
                <MenuItem>New movie</MenuItem>
            </MenuList>
        </Menu>


        <SearchButtonDialog />
        

        <Flex
            marginLeft="auto"
        >
            <Avatar size="md" name='USER' />
        </Flex>

    </Flex>
}
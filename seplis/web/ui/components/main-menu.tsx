import { ChevronDownIcon } from '@chakra-ui/icons'
import { Avatar, Box, Button, Flex, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, useDisclosure } from '@chakra-ui/react'
import { Link, useNavigate, } from 'react-router-dom'
import { MovieNew } from './movie/settings'
import { SearchButtonDialog } from './search'
import { SeriesNew } from './series/settings'

export default function MainMenu() {
    return <Flex
        backgroundColor="blackAlpha.500"
        padding="0.6rem"
        paddingLeft="1rem"
        paddingRight="1rem"
        alignItems="center"
    >
        <Link to="/">
            <Flex
                fontSize="2xl"
                color="seplis.100"
                fontWeight="600"
                marginRight="0.75rem"
            >
                SEPLIS
            </Flex>
        </Link>

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
                <SeriesNewMenuItem />
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
                <MovieNewMenuItem />
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


function SeriesNewMenuItem() {
    const { isOpen, onOpen, onClose } = useDisclosure()
    const navigate = useNavigate()

    return <>
        <MenuItem onClick={onOpen}>New series</MenuItem>
        <Modal onClose={onClose} isOpen={isOpen}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>New series</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <SeriesNew onDone={(seriesId) => {
                        onClose()
                        navigate(`/series/${seriesId}`)
                    }} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}


function MovieNewMenuItem() {
    const { isOpen, onOpen, onClose } = useDisclosure()
    const navigate = useNavigate()

    return <>
        <MenuItem onClick={onOpen}>New movie</MenuItem>
        <Modal onClose={onClose} isOpen={isOpen}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>New series</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <MovieNew onDone={(movieId) => {
                        onClose()
                        navigate(`/movies/${movieId}`)
                    }} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}
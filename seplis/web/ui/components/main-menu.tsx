import { ChevronDownIcon, HamburgerIcon } from '@chakra-ui/icons'
import { Avatar, Box, Button, Drawer, DrawerBody, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay, Flex, IconButton, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, useDisclosure } from '@chakra-ui/react'
import { IUser } from '@seplis/interfaces/user'
import { useState } from 'react'
import { Link, useNavigate, } from 'react-router-dom'
import ChangePasswordForm from './change_password_form'
import { MovieNew } from './movie/settings'
import ChromecastIcon from './player/chromecast-icon'
import { SearchButtonDialog } from './search'
import { SeriesNew } from './series/settings'

export default function MainMenu({ active }: { active?: string }) {
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

        <Flex display={['none', 'flex']}>
            <MenuItems active={active} />
        </Flex>

        <Box display={['block', 'none']} marginRight="0.75rem">
            <MobileMenu active={active} />
        </Box>

        <Box marginRight="0.75rem">
            <SearchButtonDialog />
        </Box>

        <Flex
            marginLeft="auto"
            alignItems="center"
        >
            <ChromecastIcon />
            <Menu autoSelect={false}>
                <MenuButton>
                    <UserAvatar />
                </MenuButton>
                <MenuList>
                    {ChangePasswordMenuItem()}
                    <Link to="/logout"><MenuItem>Logout</MenuItem></Link>
                </MenuList>
            </Menu>
        </Flex>
    </Flex>
}

function MobileMenu({ active }: { active?: string }) {
    const { isOpen, onOpen, onClose } = useDisclosure()
    return <>
        <IconButton
            aria-label="Menu"
            icon={<HamburgerIcon />}
            onClick={onOpen}
        />
        <Drawer
            isOpen={isOpen}
            placement='right'
            onClose={onClose}
        >
            <DrawerOverlay />
            <DrawerContent>
                <DrawerCloseButton />
                <DrawerHeader>SEPLIS</DrawerHeader>
                <DrawerBody>
                    {isOpen &&
                        <Flex direction="column" gap="1rem" justifyContent="center">
                            <MenuItems active={active} />
                        </Flex>}
                </DrawerBody>
            </DrawerContent>
        </Drawer>
    </>
}


function MenuItems({ active }: { active?: string }) {
    return <>
        <Box marginRight={["0", "0.75rem"]}>
            <Link to="/watch">
                <Button
                    variant={active == 'watch' ? 'solid' : 'ghost'}
                    width={['100%', 'auto']}
                >
                    Watch
                </Button>
            </Link>
        </Box>

        <Menu autoSelect={false}>
            <MenuButton
                variant={active == 'series' ? 'solid' : 'ghost'}
                marginRight={["0", "0.75rem"]}
                as={Button}
                rightIcon={<ChevronDownIcon />}
            >
                Series
            </MenuButton>
            <MenuList>
                <Link to="/series?sort=popularity_desc"><MenuItem>Popular</MenuItem></Link>
                <Link to="/series?sort=rating_desc"><MenuItem>Top Rated</MenuItem></Link>
                <Link to="/series/home"><MenuItem>Home</MenuItem></Link>
                <Link to="/series/watchlist"><MenuItem>Watchlist</MenuItem></Link>
                <Link to="/series/favorites"><MenuItem>Favorites</MenuItem></Link>
                <Link to="/series/watched"><MenuItem>Watched</MenuItem></Link>
                <Link to="/series/countdown"><MenuItem>Countdown</MenuItem></Link>
                <Link to="/series/recently-aired"><MenuItem>Recently aired</MenuItem></Link>
                <Link to="/series/to-watch"><MenuItem>To watch</MenuItem></Link>
                <MenuDivider />
                <SeriesNewMenuItem />
            </MenuList>
        </Menu>


        <Menu autoSelect={false}>
            <MenuButton
                variant={active == 'movies' ? 'solid' : 'ghost'}
                marginRight={["0", "0.75rem"]}
                as={Button}
                rightIcon={<ChevronDownIcon />}
            >
                Movies
            </MenuButton>
            <MenuList>
                <Link to="/movies?sort=popularity_desc"><MenuItem>Popular</MenuItem></Link>
                <Link to="/movies?sort=rating_desc"><MenuItem>Top Rated</MenuItem></Link>
                <Link to="/movies/watchlist"><MenuItem>Watchlist</MenuItem></Link>
                <Link to="/movies/favorites"><MenuItem>Favorites</MenuItem></Link>
                <Link to="/movies/watched"><MenuItem>Watched</MenuItem></Link>
                <MenuDivider />
                <MovieNewMenuItem />
            </MenuList>
        </Menu>
    </>
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
                <ModalBody paddingBottom="1.5rem">
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
                <ModalHeader>New movie</ModalHeader>
                <ModalCloseButton />
                <ModalBody paddingBottom="1.5rem">
                    <MovieNew onDone={(movieId) => {
                        onClose()
                        navigate(`/movies/${movieId}`)
                    }} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}


function ChangePasswordMenuItem() {
    const { isOpen, onOpen, onClose } = useDisclosure()

    return <>
        <MenuItem onClick={onOpen}>Change password</MenuItem>
        <Modal onClose={onClose} isOpen={isOpen}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Change password</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <ChangePasswordForm />
                </ModalBody>
                <ModalFooter></ModalFooter>
            </ModalContent>
        </Modal>
    </>
}


function UserAvatar() {
    const [user, setUser] = useState<IUser>(() => {
        const s = localStorage.getItem('activeUser')
        return JSON.parse(s)
    })
    if (!user)
        return null
    return <Avatar size="md" name={user?.username} />
}
import { Avatar, Flex, Menu } from '@mantine/core'
import {
    ArrowsClockwiseIcon,
    HardDrivesIcon,
    PlusIcon,
    SignOutIcon,
} from '@phosphor-icons/react'
import { useNavigate } from 'react-router-dom'
import {
    useActiveUser,
    useSessionActions,
    useUsersLoggedIn,
} from '../api/session.store'
import { useAddUserPopup } from '../hooks/use-add-user-popup'

export function UserMenu() {
    const navigate = useNavigate()
    const [user] = useActiveUser()
    const [usersLoggedIn] = useUsersLoggedIn()
    const { logout, switchActiveUser } = useSessionActions()
    const { openAddUserPopup } = useAddUserPopup()

    if (!user) return null

    const otherUsers = Object.values(usersLoggedIn).filter(
        (loggedInUser) => loggedInUser.id !== user.id,
    )

    return (
        <Menu width={200}>
            <Menu.Target>
                <Flex
                    align="center"
                    gap="0.5rem"
                    style={{
                        cursor: 'pointer',
                        userSelect: 'none',
                    }}
                >
                    <Avatar color="initials" size={35} name={user.username} />
                </Flex>
            </Menu.Target>
            <Menu.Dropdown>
                {otherUsers.length > 0 && (
                    <>
                        <Menu.Label>Switch user</Menu.Label>
                        {otherUsers.map((loggedInUser) => (
                            <Menu.Item
                                key={loggedInUser.id}
                                leftSection={<ArrowsClockwiseIcon size={14} />}
                                onClick={() => {
                                    switchActiveUser(loggedInUser.id)
                                }}
                            >
                                {loggedInUser.username}
                            </Menu.Item>
                        ))}
                    </>
                )}
                <Menu.Item
                    leftSection={<PlusIcon size={14} />}
                    onClick={() => {
                        openAddUserPopup()
                    }}
                >
                    Add another user
                </Menu.Item>
                <Menu.Item
                    leftSection={<SignOutIcon size={14} />}
                    onClick={() => {
                        const nextUser = logout()
                        if (!nextUser) {
                            navigate('/')
                        }
                    }}
                >
                    Logout
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item
                    leftSection={<HardDrivesIcon size={14} />}
                    onClick={() => {
                        navigate('/play-servers')
                    }}
                >
                    Play servers
                </Menu.Item>
            </Menu.Dropdown>
        </Menu>
    )
}

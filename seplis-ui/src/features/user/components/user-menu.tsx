import { Avatar, Flex, Menu } from '@mantine/core'
import { SignOutIcon } from '@phosphor-icons/react'
import { useNavigate } from 'react-router-dom'
import { logout, useActiveUser } from '../api/active-user.api'

export function UserMenu() {
    const navigate = useNavigate()
    const [user] = useActiveUser()

    if (!user) return null

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
                <Menu.Item
                    leftSection={<SignOutIcon size={14} />}
                    onClick={() => {
                        logout()
                        navigate('/login')
                    }}
                >
                    Logout
                </Menu.Item>
            </Menu.Dropdown>
        </Menu>
    )
}

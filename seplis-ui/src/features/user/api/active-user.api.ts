import { useLocalStorage } from '@mantine/hooks'
import { UsersLoggedIn } from '../types/login.types'
import { User } from '../types/user.types'

export function setActiveUser(props: { user: User; token: string }) {
    const users: UsersLoggedIn = JSON.parse(
        localStorage.getItem('users') || '{}',
    )
    users[props.user.id] = {
        ...props.user,
        token: props.token,
    }
    localStorage.setItem('users', JSON.stringify(users))
    localStorage.setItem('activeUser', JSON.stringify(props.user))
}

export function getActiveUser(): User | null {
    const activeUser = localStorage.getItem('activeUser')
    if (!activeUser) return null
    return JSON.parse(activeUser)
}

export function logout() {
    const activeUser = getActiveUser()
    if (!activeUser) return

    const users: UsersLoggedIn = JSON.parse(
        localStorage.getItem('users') || '{}',
    )
    delete users[activeUser.id]
    localStorage.setItem('users', JSON.stringify(users))
    localStorage.removeItem('activeUser')
}

export function useGetActiveUser() {
    return useLocalStorage<User | null>({
        key: 'activeUser',
        defaultValue: null,
    })
}

import { UsersLoggedIn } from '../types/login.types'
import { User } from '../types/user.types'

export function setLogin(props: { user: User; token: string }) {
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

import { setAuthorizationHeader } from '@/api'
import { IUser, IUsersLoggedIn } from '@/interfaces/user'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export function Logout() {
    const navigate = useNavigate()

    useEffect(() => {
        localStorage.removeItem('accessToken')
        setAuthorizationHeader()
        const users: IUsersLoggedIn =
            JSON.parse(localStorage.getItem('users') || 'null') || {}
        const activeUser: IUser = JSON.parse(localStorage.getItem('activeUser') || 'null')
        if (activeUser) delete users[activeUser.username]
        localStorage.setItem('users', JSON.stringify(users))
        navigate('/')
    })
    return <></>
}

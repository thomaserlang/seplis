import { useQueryClient } from '@tanstack/react-query'
import { createContext, ReactNode, useContext, useRef, useState } from 'react'
import { UserLoggedIn, UsersLoggedIn } from '../types/login.types'
import { User } from '../types/user.types'

interface SessionState {
    activeUser: User | null
    usersLoggedIn: UsersLoggedIn
}

interface SessionContextValue extends SessionState {
    logout: () => User | null
    refreshSession: () => void
    setAccessToken: (token: string | null) => void
    setActiveUser: (props: { user: User; token: string }) => void
    switchActiveUser: (userId: number) => User | null
}

const SessionContext = createContext<SessionContextValue | null>(null)

export function SessionProvider({ children }: { children: ReactNode }) {
    const queryClient = useQueryClient()
    const [sessionState, setSessionState] = useState(readSessionState)
    const sessionStateRef = useRef(sessionState)
    sessionStateRef.current = sessionState

    const updateSession = (
        nextState: SessionState,
        accessToken?: string | null,
    ) => {
        persistUsersLoggedIn(nextState.usersLoggedIn)
        persistActiveUser(nextState.activeUser)
        if (accessToken !== undefined) {
            persistAccessToken(accessToken)
        }
        setSessionState(nextState)
        queryClient.invalidateQueries({})
    }

    const value: SessionContextValue = {
        activeUser: sessionState.activeUser,
        usersLoggedIn: sessionState.usersLoggedIn,
        logout: () => {
            const activeUser = sessionStateRef.current.activeUser
            if (!activeUser) return null

            const usersLoggedIn = { ...sessionStateRef.current.usersLoggedIn }
            delete usersLoggedIn[activeUser.id]

            const nextUser = Object.values(usersLoggedIn)[0]
            const nextActiveUser = nextUser ? userToActiveUser(nextUser) : null

            updateSession(
                {
                    activeUser: nextActiveUser,
                    usersLoggedIn,
                },
                nextUser?.token ?? null,
            )

            return nextActiveUser
        },
        refreshSession: () => {
            setSessionState(readSessionState())
            queryClient.invalidateQueries({})
        },
        setAccessToken: (token: string | null) => {
            persistAccessToken(token)
        },
        setActiveUser: ({ user, token }: { user: User; token: string }) => {
            const usersLoggedIn = {
                ...sessionStateRef.current.usersLoggedIn,
                [user.id]: {
                    ...user,
                    token,
                },
            }

            updateSession(
                {
                    activeUser: user,
                    usersLoggedIn,
                },
                token,
            )
        },
        switchActiveUser: (userId: number) => {
            const user = sessionStateRef.current.usersLoggedIn[userId]
            if (!user) return null

            const activeUser = userToActiveUser(user)
            updateSession(
                {
                    activeUser,
                    usersLoggedIn: sessionStateRef.current.usersLoggedIn,
                },
                user.token,
            )

            return activeUser
        },
    }

    return (
        <SessionContext.Provider value={value}>
            {children}
        </SessionContext.Provider>
    )
}

export function useSession() {
    const value = useContext(SessionContext)
    if (!value) {
        throw new Error('useSession must be used within SessionProvider')
    }
    return value
}

export function useActiveUser() {
    const { activeUser } = useSession()
    return [activeUser] as const
}

export function useUsersLoggedIn() {
    const { usersLoggedIn } = useSession()
    return [usersLoggedIn] as const
}

export function useSessionActions() {
    const {
        logout,
        refreshSession,
        setAccessToken,
        setActiveUser,
        switchActiveUser,
    } = useSession()

    return {
        logout,
        refreshSession,
        setAccessToken,
        setActiveUser,
        switchActiveUser,
    }
}

export function readUsersLoggedIn(): UsersLoggedIn {
    return JSON.parse(localStorage.getItem('users') || '{}')
}

export function readActiveUser(): User | null {
    const activeUser = localStorage.getItem('activeUser')
    if (!activeUser) return null
    return JSON.parse(activeUser)
}

function readSessionState(): SessionState {
    return {
        activeUser: readActiveUser(),
        usersLoggedIn: readUsersLoggedIn(),
    }
}

function persistUsersLoggedIn(usersLoggedIn: UsersLoggedIn) {
    localStorage.setItem('users', JSON.stringify(usersLoggedIn))
}

function persistActiveUser(activeUser: User | null) {
    if (activeUser) {
        localStorage.setItem('activeUser', JSON.stringify(activeUser))
    } else {
        localStorage.removeItem('activeUser')
    }
}

function persistAccessToken(token: string | null) {
    if (token) {
        localStorage.setItem('accessToken', token)
    } else {
        localStorage.removeItem('accessToken')
    }
}

function userToActiveUser(user: UserLoggedIn): User {
    return {
        id: user.id,
        username: user.username,
        created_at: user.created_at,
        scopes: user.scopes,
    }
}

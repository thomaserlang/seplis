export interface RequestResetPasswordCreate {
    email: string
}

export interface ResetPasswordCreate {
    key: string
    new_password: string
}

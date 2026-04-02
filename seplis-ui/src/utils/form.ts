import { APIError } from '@/types/api-error.types'
import { UseFormReturnType } from '@mantine/form'

export function setFormErrors(form: UseFormReturnType<any>, error: APIError) {
    for (const e of error?.errors) {
        form.setFieldError(e.field, e.message)
    }
}

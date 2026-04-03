import { UseFormReturnType } from '@mantine/form'

export function setFormErrors(form: UseFormReturnType<any>, error: any) {
    for (const e of error?.data?.errors) {
        const field = Array.isArray(e.field)
            ? e.field.slice(1).join('.')
            : e.field.split('.').slice(1).join('.')
        form.setFieldError(field, e.message)
    }
}

import { ErrorBox } from '@/components/error-box'
import { queryClient } from '@/queryclient'
import { toastError, toastSuccess } from '@/utils/toast'
import { Box, Button, Flex, TextInput, Title } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useAcceptPlayServerInvite } from '../api/play-server-invites.api'
import { playServersQueryKey } from '../api/play-servers.api'

interface Props {
    initialInviteId?: string
    onAccepted?: () => void
}

export function PlayServerAcceptInviteForm({
    initialInviteId = '',
    onAccepted,
}: Props) {
    const form = useForm({
        mode: 'uncontrolled',
        initialValues: {
            invite_id: initialInviteId,
        },
    })
    const accept = useAcceptPlayServerInvite({
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: playServersQueryKey({}),
            })
            toastSuccess('Invite accepted')
            onAccepted?.()
        },
        onError: (error) => {
            toastError(error)
        },
    })

    return (
        <Box bd="1px solid var(--mantine-color-default-border)" bdrs="lg" p="xl" maw={520}>
            <Title order={2} mb={4}>
                Accept play server invite
            </Title>
            <form
                onSubmit={form.onSubmit(({ invite_id }) => {
                    accept.mutate({
                        data: {
                            invite_id,
                        },
                    })
                })}
            >
                <Flex direction="column" gap="md">
                    <TextInput
                        label="Invite id"
                        required
                        autoFocus
                        key={form.key('invite_id')}
                        {...form.getInputProps('invite_id')}
                    />
                    {accept.error && <ErrorBox errorObj={accept.error} />}
                    <Flex justify="flex-end">
                        <Button type="submit" loading={accept.isPending}>
                            Accept invite
                        </Button>
                    </Flex>
                </Flex>
            </form>
        </Box>
    )
}

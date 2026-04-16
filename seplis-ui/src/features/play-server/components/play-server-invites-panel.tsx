import { ErrorBox } from '@/components/error-box'
import { getUsers } from '@/features/user'
import { pageItemsFlatten } from '@/utils/api-crud'
import { queryClient } from '@/queryclient'
import { toastError, toastSuccess } from '@/utils/toast'
import {
    CopyButton,
    ActionIcon,
    Button,
    Flex,
    Table,
    Text,
    TextInput,
} from '@mantine/core'
import { openConfirmModal } from '@mantine/modals'
import { CheckIcon, CopyIcon, TrashIcon } from '@phosphor-icons/react'
import { useForm } from '@mantine/form'
import {
    playServerInvitesQueryKey,
    useCreatePlayServerInvite,
    useDeletePlayServerInvite,
    useGetPlayServerInvites,
} from '../api/play-server-invites.api'

interface Props {
    playServerId: string
}

export function PlayServerInvitesPanel({ playServerId }: Props) {
    const form = useForm({
        mode: 'uncontrolled',
        initialValues: {
            username: '',
        },
    })
    const { data, error, isLoading } = useGetPlayServerInvites({
        playServerId,
        params: {
            per_page: 100,
        },
    })
    const createInvite = useCreatePlayServerInvite({
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: playServerInvitesQueryKey({ playServerId }),
            })
        },
    })
    const deleteInvite = useDeletePlayServerInvite({
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: playServerInvitesQueryKey({ playServerId }),
            })
            toastSuccess('Invite removed')
        },
        onError: (error) => {
            toastError(error)
        },
    })

    const invites = pageItemsFlatten(data)
    const latestInviteId = createInvite.data?.invite_id
    const inviteUrl =
        latestInviteId && typeof window !== 'undefined'
            ? `${window.location.origin}/play-servers/accept-invite?invite_id=${latestInviteId}`
            : null

    return (
        <>
            <form
                onSubmit={form.onSubmit(async ({ username }) => {
                    const normalizedUsername = username.trim()
                    if (!normalizedUsername) {
                        form.setFieldError('username', 'Enter a username')
                        return
                    }

                    try {
                        const users = await getUsers({
                            params: {
                                username: normalizedUsername,
                            },
                        })
                        const user = users.find(
                            (user) => user.username === normalizedUsername,
                        )

                        if (!user) {
                            form.setFieldError(
                                'username',
                                'No user found with that username',
                            )
                            return
                        }

                        await createInvite.mutateAsync({
                            playServerId,
                            data: {
                                user_id: user.id,
                            },
                        })
                        toastSuccess('Invite created')
                        form.reset()
                    } catch (error) {
                        toastError(error)
                    }
                })}
            >
                <Flex gap="sm" align="flex-end" wrap="wrap" mb="md">
                    <TextInput
                        label="Username"
                        placeholder="someone"
                        w={{ base: '100%', sm: 220 }}
                        key={form.key('username')}
                        {...form.getInputProps('username')}
                    />
                    <Button type="submit" loading={createInvite.isPending}>
                        Create invite
                    </Button>
                </Flex>
            </form>

            {inviteUrl && (
                <Flex direction="column" gap="xs" mb="md">
                    <Text size="sm">Send this link to the user.</Text>
                    <Flex gap="sm" align="center">
                        <TextInput value={inviteUrl} readOnly flex={1} />
                        <CopyValueButton value={inviteUrl} />
                    </Flex>
                </Flex>
            )}

            {error && <ErrorBox errorObj={error} />}
            {!error && isLoading && <></>}
            {!error && !isLoading && invites.length === 0 && <></>}
            {!error && invites.length > 0 && (
                <Table.ScrollContainer
                    minWidth={500}
                    style={{
                        borderRadius: 'var(--mantine-radius-sm)',
                        overflow: 'hidden',
                    }}
                >
                    <Table withTableBorder highlightOnHover>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>User</Table.Th>
                                <Table.Th>Created</Table.Th>
                                <Table.Th>Expires</Table.Th>
                                <Table.Th />
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {invites.map((invite) => (
                                <Table.Tr
                                    key={`${invite.user.id}-${invite.created_at}`}
                                >
                                    <Table.Td>{invite.user.username}</Table.Td>
                                    <Table.Td>{formatDate(invite.created_at)}</Table.Td>
                                    <Table.Td>{formatDate(invite.expires_at)}</Table.Td>
                                    <Table.Td>
                                        <ActionIcon
                                            color="red.5"
                                            variant="subtle"
                                            loading={
                                                deleteInvite.isPending &&
                                                deleteInvite.variables?.userId ===
                                                    String(invite.user.id)
                                            }
                                            onClick={() => {
                                                openConfirmModal({
                                                    title: 'Remove invite',
                                                    children: `Remove invite for ${invite.user.username}?`,
                                                    labels: {
                                                        confirm: 'Remove',
                                                        cancel: 'Cancel',
                                                    },
                                                    confirmProps: {
                                                        color: 'red.5',
                                                    },
                                                    onConfirm: async () => {
                                                        await deleteInvite.mutateAsync({
                                                            playServerId,
                                                            userId: String(invite.user.id),
                                                        })
                                                    },
                                                })
                                            }}
                                        >
                                            <TrashIcon size={16} />
                                        </ActionIcon>
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                    </Table.ScrollContainer>
            )}
        </>
    )
}

function CopyValueButton({ value }: { value: string }) {
    return (
        <CopyButton value={value}>
            {({ copied, copy }) => (
                <ActionIcon variant="light" onClick={copy}>
                    {copied ? <CheckIcon size={16} /> : <CopyIcon size={16} />}
                </ActionIcon>
            )}
        </CopyButton>
    )
}

function formatDate(value: string) {
    return new Date(value).toLocaleString()
}

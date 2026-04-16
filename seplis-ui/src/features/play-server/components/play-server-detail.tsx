import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { queryClient } from '@/queryclient'
import { toastError, toastSuccess } from '@/utils/toast'
import {
    Button,
    Flex,
    Modal,
    Stack,
    Tabs,
    Text,
    Title,
} from '@mantine/core'
import { openConfirmModal } from '@mantine/modals'
import { ArrowLeftIcon, PencilSimpleIcon, TrashIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
    playServerQueryKey,
    useDeletePlayServer,
    useGetPlayServer,
    useUpdatePlayServer,
} from '../api/play-server.api'
import { playServersQueryKey } from '../api/play-servers.api'
import { PlayServerForm, PlayServerFormValues } from './play-server-form'
import { PlayServerAccessPanel } from './play-server-access-panel'
import { PlayServerInvitesPanel } from './play-server-invites-panel'

interface Props {
    playServerId: string
    onClose?: () => void
}

export function PlayServerDetail({ playServerId, onClose }: Props) {
    const navigate = useNavigate()
    const [editing, setEditing] = useState(false)
    const { data, isLoading, error } = useGetPlayServer({
        playServerId,
    })

    const update = useUpdatePlayServer({
        onSuccess: async () => {
            await Promise.all([
                queryClient.invalidateQueries({
                    queryKey: playServerQueryKey({ playServerId }),
                }),
                queryClient.invalidateQueries({
                    queryKey: playServersQueryKey({}),
                }),
            ])
            toastSuccess('Play server updated')
            setEditing(false)
        },
        onError: (error) => {
            toastError(error)
        },
    })
    const del = useDeletePlayServer({
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: playServersQueryKey({}),
            })
            toastSuccess('Play server deleted')
            if (onClose) {
                onClose()
                return
            }
            navigate('/play-servers')
        },
        onError: (error) => {
            toastError(error)
        },
    })

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data) return <ErrorBox message="Play server not found" />

    return (
        <Stack gap="lg">
            {!onClose && (
                <Button
                    component={Link}
                    to="/play-servers"
                    variant="subtle"
                    leftSection={<ArrowLeftIcon size={16} />}
                    w="fit-content"
                >
                    Back to play servers
                </Button>
            )}

            <Flex justify="space-between" align="center" wrap="wrap" gap="sm">
                <Stack gap={4}>
                    <Title order={2}>{data.name}</Title>
                    <Text>{data.url}</Text>
                </Stack>
                <Flex gap="sm">
                    <Button
                        variant="default"
                        leftSection={<PencilSimpleIcon size={16} />}
                        onClick={() => setEditing((v) => !v)}
                    >
                        {editing ? 'Close editor' : 'Edit'}
                    </Button>
                    <Button
                        color="red.5"
                        variant="light"
                        leftSection={<TrashIcon size={16} />}
                        loading={del.isPending}
                        onClick={() => {
                            openConfirmModal({
                                title: 'Delete play server',
                                children: `Delete play server "${data.name}"?`,
                                labels: {
                                    confirm: 'Delete',
                                    cancel: 'Cancel',
                                },
                                confirmProps: {
                                    color: 'red.5',
                                },
                                onConfirm: async () => {
                                    await del.mutateAsync({ playServerId })
                                },
                            })
                        }}
                    >
                        Delete
                    </Button>
                </Flex>
            </Flex>

            <Tabs defaultValue="invites">
                <Tabs.List>
                    <Tabs.Tab value="invites">Invites</Tabs.Tab>
                    <Tabs.Tab value="access">Access</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="invites" pt="md">
                    <PlayServerInvitesPanel playServerId={playServerId} />
                </Tabs.Panel>
                <Tabs.Panel value="access" pt="md">
                    <PlayServerAccessPanel playServerId={playServerId} />
                </Tabs.Panel>
            </Tabs>

            <Modal
                opened={editing}
                onClose={() => setEditing(false)}
                title="Edit play server"
            >
                <PlayServerForm
                    initialValues={{
                        name: data.name,
                        url: data.url,
                        secret: '',
                    }}
                    submitLabel="Save changes"
                    loading={update.isPending}
                    error={update.error}
                    secretRequired={false}
                    onCancel={() => setEditing(false)}
                    onSubmit={(values: PlayServerFormValues) => {
                        update.mutate({
                            playServerId,
                            data: {
                                name: values.name,
                                url: values.url,
                                secret: values.secret.trim() || undefined,
                            },
                        })
                    }}
                />
            </Modal>
        </Stack>
    )
}

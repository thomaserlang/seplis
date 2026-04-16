import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { queryClient } from '@/queryclient'
import { pageItemsFlatten } from '@/utils/api-crud'
import { toastError, toastSuccess } from '@/utils/toast'
import {
    ActionIcon,
    Box,
    Button,
    Flex,
    Modal,
    SimpleGrid,
    Stack,
    Text,
    Title,
} from '@mantine/core'
import { openConfirmModal } from '@mantine/modals'
import { SignOutIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import {
    accessiblePlayServersQueryKey,
    useGetAccessiblePlayServers,
    useLeavePlayServer,
} from '../api/play-server-access.api'
import {
    useCreatePlayServer,
} from '../api/play-server.api'
import {
    playServersQueryKey,
    useGetPlayServers,
} from '../api/play-servers.api'
import { PlayServerDetail } from './play-server-detail'
import { PlayServerForm, PlayServerFormValues } from './play-server-form'

export function PlayServerList() {
    const [creating, setCreating] = useState(false)
    const [managingId, setManagingId] = useState<string | null>(null)
    const { data, isLoading, error } = useGetPlayServers({
        params: {
            per_page: 100,
        },
    })
    const {
        data: sharedData,
        isLoading: isLoadingShared,
        error: sharedError,
    } = useGetAccessiblePlayServers({
        params: {
            per_page: 100,
        },
    })

    const create = useCreatePlayServer({
        onSuccess: async (server) => {
            await queryClient.invalidateQueries({
                queryKey: playServersQueryKey({}),
            })
            toastSuccess('Play server created')
            setCreating(false)
            setManagingId(server.id)
        },
        onError: (error) => {
            toastError(error)
        },
    })
    const leave = useLeavePlayServer({
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: accessiblePlayServersQueryKey({}),
            })
            toastSuccess('Access removed')
        },
        onError: (error) => {
            toastError(error)
        },
    })

    const servers = pageItemsFlatten(data)
    const sharedServers = pageItemsFlatten(sharedData)

    return (
        <Stack gap="lg">
            <Box bd="1px solid var(--mantine-color-default-border)" bdrs="lg" p="xl">
                <Flex justify="space-between" align="center" gap="md" wrap="wrap" mb="md">
                    <Title order={4}>Owned</Title>
                    <Button onClick={() => setCreating(true)}>Add</Button>
                </Flex>

                {isLoading && <PageLoader />}
                {error && <ErrorBox errorObj={error} />}
                {!isLoading && !error && servers.length === 0 && <></>}
                {!error && servers.length > 0 && (
                    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg" mb="xl">
                        {servers.map((server) => (
                            <Box
                                key={server.id}
                                bd="1px solid var(--mantine-color-default-border)"
                                bdrs="lg"
                                p="lg"
                            >
                                <Flex align="center" justify="space-between" gap="md">
                                    <Text fw={700}>{server.name}</Text>
                                    <Button
                                        variant="subtle"
                                        onClick={() => setManagingId(server.id)}
                                    >
                                        Manage
                                    </Button>
                                </Flex>
                            </Box>
                        ))}
                    </SimpleGrid>
                )}
            </Box>

            <Box bd="1px solid var(--mantine-color-default-border)" bdrs="lg" p="xl">
                <Title order={4} mb="md">
                    Shared
                </Title>

                {isLoadingShared && <PageLoader />}
                {sharedError && <ErrorBox errorObj={sharedError} />}
                {!isLoadingShared && !sharedError && sharedServers.length === 0 && <></>}

                {!sharedError && sharedServers.length > 0 && (
                    <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
                        {sharedServers.map((server) => (
                            <Box
                                key={server.id}
                                bd="1px solid var(--mantine-color-default-border)"
                                bdrs="lg"
                                p="lg"
                            >
                                <Flex align="center" justify="space-between" gap="md">
                                    <Box style={{ minWidth: 0 }}>
                                        <Text fw={700}>{server.name}</Text>
                                        <Text c="dimmed" size="sm">
                                            {server.url}
                                        </Text>
                                    </Box>
                                    <ActionIcon
                                        color="red"
                                        variant="subtle"
                                        loading={
                                            leave.isPending &&
                                            leave.variables?.playServerId === server.id
                                        }
                                        onClick={() => {
                                            openConfirmModal({
                                                title: 'Remove access',
                                                children: `Remove your access to "${server.name}"?`,
                                                labels: {
                                                    confirm: 'Remove',
                                                    cancel: 'Cancel',
                                                },
                                                confirmProps: {
                                                    color: 'red.5',
                                                },
                                                onConfirm: async () => {
                                                    await leave.mutateAsync({
                                                        playServerId: server.id,
                                                    })
                                                },
                                            })
                                        }}
                                    >
                                        <SignOutIcon size={16} />
                                    </ActionIcon>
                                </Flex>
                            </Box>
                        ))}
                    </SimpleGrid>
                )}
            </Box>

            <Modal
                opened={creating}
                onClose={() => setCreating(false)}
                title="Add play server"
            >
                <PlayServerForm
                    initialValues={{
                        name: '',
                        url: '',
                        secret: '',
                    }}
                    submitLabel="Create play server"
                    loading={create.isPending}
                    error={create.error}
                    onCancel={() => setCreating(false)}
                    onSubmit={(values: PlayServerFormValues) => {
                        create.mutate({
                            data: values,
                        })
                    }}
                />
            </Modal>

            <Modal
                opened={!!managingId}
                onClose={() => setManagingId(null)}
                title="Server"
                size="xl"
            >
                {managingId && (
                    <PlayServerDetail
                        playServerId={managingId}
                        onClose={() => setManagingId(null)}
                    />
                )}
            </Modal>
        </Stack>
    )
}

import { ErrorBox } from '@/components/error-box'
import { pageItemsFlatten } from '@/utils/api-crud'
import { queryClient } from '@/queryclient'
import { toastError, toastSuccess } from '@/utils/toast'
import { ActionIcon, Table } from '@mantine/core'
import { openConfirmModal } from '@mantine/modals'
import { TrashIcon } from '@phosphor-icons/react'
import {
    playServerAccessQueryKey,
    useGetPlayServerAccess,
    useRemovePlayServerAccess,
} from '../api/play-server-access.api'

interface Props {
    playServerId: string
}

export function PlayServerAccessPanel({ playServerId }: Props) {
    const { data, error, isLoading } = useGetPlayServerAccess({
        playServerId,
        params: {
            per_page: 100,
        },
    })
    const removeAccess = useRemovePlayServerAccess({
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: playServerAccessQueryKey({ playServerId }),
            })
        },
    })

    const access = pageItemsFlatten(data)

    return (
        <>
            {error && <ErrorBox errorObj={error} />}
            {!error && isLoading && <></>}
            {!error && !isLoading && access.length === 0 && <></>}
            {!error && access.length > 0 && (
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
                                <Table.Th>Granted</Table.Th>
                                <Table.Th />
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {access.map((entry) => (
                                <Table.Tr key={`${entry.user.id}-${entry.created_at}`}>
                                    <Table.Td>{entry.user.username}</Table.Td>
                                    <Table.Td>{formatDate(entry.created_at)}</Table.Td>
                                    <Table.Td>
                                        <ActionIcon
                                            color="red.5"
                                            variant="subtle"
                                            loading={
                                                removeAccess.isPending &&
                                                removeAccess.variables?.userId ===
                                                    String(entry.user.id)
                                            }
                                            onClick={() => {
                                                openConfirmModal({
                                                    title: 'Remove access',
                                                    children: `Remove ${entry.user.username} from this play server?`,
                                                    labels: {
                                                        confirm: 'Remove',
                                                        cancel: 'Cancel',
                                                    },
                                                    confirmProps: {
                                                        color: 'red.5',
                                                    },
                                                    onConfirm: async () => {
                                                        try {
                                                            await removeAccess.mutateAsync({
                                                                playServerId,
                                                                userId: String(entry.user.id),
                                                            })
                                                            toastSuccess('Access removed')
                                                        } catch (error) {
                                                            toastError(error)
                                                        }
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

function formatDate(value: string) {
    return new Date(value).toLocaleString()
}

import { Divider, Group, Stack, Text, Title, Tooltip } from '@mantine/core'

interface StatRow {
    label: string
    value: string
    description?: string
}

export function WatchStatsSummary({
    title,
    rows,
}: {
    title: string
    rows: StatRow[]
}) {
    return (
        <Stack gap="sm">
            <Title order={3} size="h4">
                {title}
            </Title>
            <Divider />
            {rows.map(({ label, value, description }) => (
                <Group
                    key={label}
                    justify="space-between"
                    gap="xs"
                    align="baseline"
                    wrap="nowrap"
                >
                    <Tooltip
                        label={description}
                        disabled={!description}
                        multiline
                        maw={260}
                        events={{ hover: true, focus: true, touch: true }}
                    >
                        <Text c="dimmed" tabIndex={description ? 0 : undefined}>
                            {label}
                        </Text>
                    </Tooltip>
                    <Text
                        fw={600}
                        ta="right"
                        style={{ fontVariantNumeric: 'tabular-nums' }}
                    >
                        {value}
                    </Text>
                </Group>
            ))}
        </Stack>
    )
}

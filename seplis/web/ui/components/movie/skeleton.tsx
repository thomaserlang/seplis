import { Skeleton, Stack } from "@chakra-ui/react";

export function MovieSkeleton() {
    return <Stack direction="row" spacing="1rem" maxWidth="1100px">
        <div className="poster-container-sizing">
            <div className="poster-container" style={{ 'flexShrink': '0' }}>
                <Skeleton height="100%" borderRadius="md" />
            </div>
        </div>
        <Stack marginLeft="1rem" width="100%" direction="column">
            <Skeleton height="40px" borderRadius="md" />
            <Skeleton marginTop="1rem"  borderRadius="md" flex="1 1 auto" />
        </Stack>
    </Stack>
}
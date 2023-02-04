import { Flex, Skeleton } from "@chakra-ui/react";

export function MovieSkeleton() {
    return <Flex>
        <div className="poster-container-sizing">
            <div className="poster-container" style={{ 'flexShrink': '0' }}>
                <Skeleton height="100%" />
            </div>
        </div>
        <Flex marginLeft="1rem" width="800px" direction="column">
            <Skeleton height="40px" />
            <Skeleton marginTop="1rem" flex="1 1 auto" />
        </Flex>
    </Flex>
}
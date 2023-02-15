import { Box, Modal, ModalBody, ModalCloseButton, ModalContent, ModalOverlay, useDisclosure } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import List from '@seplis/components/list'
import MainMenu from '@seplis/components/main-menu'
import Series from '@seplis/components/series/series'
import { ISeries, ISeriesUser } from '@seplis/interfaces/series'
import { setTitle } from '@seplis/utils'
import { useEffect, useState } from 'react'


export default function SeriesFollowing() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [series, setSeries] = useState<ISeries>(null)
    
    useEffect(() => {
        setTitle('Series Following')
    }, [])

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    return <>
        <MainMenu />

        <FocusContext.Provider value={focusKey}>
            <Box margin={["1rem"]} ref={ref}>
                <List<ISeriesUser>
                    title="Following"
                    url="/2/users/me/series-following"
                    urlParams={{
                        'per_page': 50,
                    }}
                    parseItem={(item) => (
                        {
                            key: `series-${item.series.id}`,
                            title: item.series.title,
                            img: item.series.poster_image?.url,
                        }
                    )}
                    onItemSelected={(item: ISeriesUser) => {
                        setSeries(item.series)
                        onOpen()
                    }}
                />
            </Box>
        </FocusContext.Provider>

        <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent maxWidth="1100px" backgroundColor="gray.900" padding="1rem 0">
                <ModalCloseButton />
                <ModalBody>
                    <Series series={series} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}
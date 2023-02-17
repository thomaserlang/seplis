import { Box, Modal, ModalBody, ModalCloseButton, ModalContent, ModalOverlay, useDisclosure } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import ImageList from '@seplis/components/list'
import { SeriesLoad } from '@seplis/components/series/series'
import { ISeries, ISeriesUser } from '@seplis/interfaces/series'
import { useEffect, useState } from 'react'
import { NumberParam, StringParam, useQueryParams, withDefault } from 'use-query-params'
import { SeriesUserFilter } from '../../components/series/user-filter'


export default function SeriesUserList({ title, url }: { title: string, url: string }) {
    const { ref, focusKey, focusSelf } = useFocusable()
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [series, setSeries] = useState<ISeries>(null)

    const [query, setQuery] = useQueryParams({
        sort: withDefault(StringParam, ""),
        genre_id: withDefault(NumberParam, 0),
    })

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    return <>
        <FocusContext.Provider value={focusKey}>
            <Box ref={ref}>
                <ImageList<ISeriesUser>
                    title={title}
                    url={url}
                    urlParams={{
                        ...query,
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
                    renderFilter={(options) => {
                        return <SeriesUserFilter defaultValue={query} onSubmit={(data) => {
                            setQuery(data)
                            options.onClose()
                        }} />
                    }}
                />
            </Box>
        </FocusContext.Provider>

        <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent maxWidth="1100px" backgroundColor="gray.900" padding="1rem 0">
                <ModalCloseButton />
                <ModalBody>
                    {isOpen && <SeriesLoad seriesId={series.id} />}
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}

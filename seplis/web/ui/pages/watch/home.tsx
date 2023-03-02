import { Stack } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { ISeriesAndEpisode, ISeriesUser } from '@seplis/interfaces/series'
import { episodeNumber, setTitle } from '@seplis/utils'
import { useCallback, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'


export default function WatchHome() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        setTitle('Watch Home')
    }, [])

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    const onRowFocus = useCallback(({ y }: { y: number }) => {
        window.scrollTo({
            top: y,
            behavior: 'smooth'
        });
    }, [ref])

    const itemSelected = (item: ISeriesUser | ISeriesAndEpisode) => {
        navigate(`/series/${item.series.id}`, {state: {
            background: location
        }})
    }

    return <>
        <MainMenu />
        
        <FocusContext.Provider value={focusKey}>

            <Stack ref={ref} marginTop="0.5rem" marginBottom="0.5rem">

                <Slider<ISeriesAndEpisode>
                    title="Series to Watch"
                    url="/2/users/me/series-to-watch?can_watch=true"
                    parseItem={(item) => (
                        {
                            key: `series-${item.series.id}`,
                            title: item.series.title,
                            img: item.series.poster_image?.url,
                            bottomText: episodeNumber(item.episode),
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />


            </Stack>
        </FocusContext.Provider>
    </>
}
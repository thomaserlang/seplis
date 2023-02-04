import SliderSeriesFollowing from "@seplis/components/slider-series-following"
import SliderWatched from "@seplis/components/slider-watched"
import { useCallback, useEffect } from "react"
import { FocusContext, useFocusable } from "@noriginmedia/norigin-spatial-navigation"

export default function Home() {
    const { ref, focusKey, focusSelf } = useFocusable()
    
    useEffect(() => {
        document.title = 'Home | SEPLIS'
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
      
    return <FocusContext.Provider value={focusKey}>
        <div ref={ref}>
            <SliderWatched onFocus={onRowFocus} />
            <SliderSeriesFollowing onFocus={onRowFocus} />
        </div>
    </FocusContext.Provider>
}
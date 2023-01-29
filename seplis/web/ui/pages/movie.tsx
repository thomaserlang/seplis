import api from "@seplis/api"
import { Box, Flex, Heading, Tag } from "@chakra-ui/react"
import { IMovie } from "@seplis/interfaces/movie"
import { setTitle } from "@seplis/utils"
import { useQuery } from "@tanstack/react-query"
import { useParams } from "react-router-dom"
import { StarIcon } from "@chakra-ui/icons"
import { Poster } from "@seplis/components/poster"
import StaredButton from "@seplis/components/movie/stared-button"


export default function Movie() {
    const { movieId } = useParams()
    const { isInitialLoading, data } = useQuery<IMovie>([movieId], async () => {
        const data = await api.get<IMovie>(`/2/movies/${movieId}`)
        setTitle(data.data.title)
        return data.data
    })
    
    if (isInitialLoading)
        return <div>LODAING</div>

    return <Flex direction={"column"} rowGap="0.5rem">
            <Flex columnGap="1rem">
                <div className="poster-container-sizing">
                    <div className="poster-container" style={{'flexShrink': '0'}}>
                        <Poster url={`${data.poster_image?.url}@SX320.webp`} title={data.title} />
                    </div>
                </div>

                <Flex direction="column" rowGap="0.5rem">
                    <Flex columnGap="0.5rem" justifyContent="flex-start">
                        <Heading>{data.title || '<Missing title>'}</Heading>
                        <Box marginLeft="auto"><StaredButton movieId={data.id} /></Box>                        
                    </Flex>
                    {data.original_title != data.title && <Heading as="h2">data.original_title</Heading>}

                    <Flex columnGap="0.5rem" rowGap="0.5rem" direction="row" wrap="wrap">
                        <div>
                            {data.release_date && <strong>{data.release_date.substring(0, 4)}</strong>}
                        </div>
                        <div>
                            {secondsToHourMin(data.runtime)}
                        </div>
                        <div>                    
                            {langCodeToLang(data.language)}
                        </div>
                        <div>
                            {data.rating} <StarIcon boxSize={2} />
                        </div>
                    </Flex>

                    <Flex columnGap="0.5rem" rowGap="0.5rem" direction="row" wrap="wrap">
                        {data.genres.map(genre => (
                            <Tag key={genre.id}>{genre.name}</Tag>
                        ))}
                    </Flex>


                    <div><i>{data.tagline}</i></div>

                    <div style={{maxWidth: '800px'}}>
                        {data.plot}
                    </div>                   
                </Flex>
        </Flex>
    </Box>
}

function secondsToHourMin(minutes: number) {
    if (!minutes)
        return
    const hours = Math.floor(minutes / 60)
    const minutesLeft = minutes % 60
    let s = ''
    if (hours > 0)
        s += `${hours}h`
    if (minutes > 0)
        s += ` ${minutesLeft}m`
    return s.trim()
}

function langCodeToLang(code: string) {
    return new Intl.DisplayNames(['en'], { type: 'language' }).of(code)
}
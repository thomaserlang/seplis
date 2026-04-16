export interface PlayIdInfoBase {
    exp: string
}

export interface PlayIdInfoEpisode extends PlayIdInfoBase {
    type: 'series'
    series_id: number
    number: number
}

export interface PlayIdInfoMovie extends PlayIdInfoBase {
    type: 'movie'
    movie_id: number
}

export type PlayIdInfo = PlayIdInfoEpisode | PlayIdInfoMovie

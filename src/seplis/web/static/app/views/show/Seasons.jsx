import React from 'react'
import qs from 'query-string'

import SeasonList from 'components/shows/episodes/SeasonList'
import {request} from 'api'
import {isAuthed} from 'utils'

class Seasons extends React.Component {

    constructor(props) {
        super(props);
        this.onSeasonChange = this.seasonChange.bind(this);
        this.state = {
            season: null,
        }
    }

    componentDidMount() {
        this.setQuerySeason()
    }

    componentDidUpdate(prevProps) {
        if (this.props.location !== prevProps.location) {
            this.setQuerySeason()
        }
    }

    setQuerySeason() {
        let q = qs.parse(location.search)
        let season = parseInt(q.season) || null

        if (season) {
            this.setState({season: season})
            return
        }

        if (this.props.show.seasons.length > 0)
            season = this.props.show.seasons[0].season
        if (isAuthed()) {
            request(
                `/1/shows/${this.props.show.id}/episodes/last-watched`
            ).done(episode => {
                this.setState({season: episode?episode.season:season})
            }).fail(() => {
                this.setState({season: season})
            })
        } else {
            this.setState({season: season})
        }
    }

    seasonChange(season) {
        this.setState({
            season: season,
        })
        this.props.history.push(`${this.props.location.pathname}?season=${season}`)
    }

    render() {
        if (!this.state.season)
            return null
        return (
            <SeasonList
                key={this.state.season}
                showId={this.props.show.id}
                seasons={this.props.show.seasons}
                seasonNumber={this.state.season}
                onSeasonChange={this.onSeasonChange}
            />
        )
    }
}

export default Seasons;
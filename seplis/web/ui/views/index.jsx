import React from 'react'
import {Route} from 'react-router-dom'

import Navbar from '../components/Navbar'
import Show from './show/Show'
import ShowNew from './show/New'
import Following from './Following'
import RecentlyAired from './RecentlyAired'
import ShowsWatched from './ShowsWatched'
import Countdown from './Countdown'
import EpisodesToWatch from './EpisodesToWatch'
import Main from './Main'
import AirDates from './AirDates'
import Account from './Account'
import Password from './Password'
import PlayServers from './PlayServers'
import PlayServer from './PlayServer'
import UserShowsStats from './UserShowsStats'
import MovieNew from './movie/New'
import Movie from './movie'
import MoviesWatched from './movie/Watched'
import MoviesStared from './movie/Stared'


class Index extends React.Component {

    render() {
        return <>
            <Navbar />
            <div className="container">
                <Route path="/show/:showId" component={Show} />
                <Route path="/show-new" component={ShowNew} />
                <Route path="/following" component={Following} />
                <Route path="/recently-aired" component={RecentlyAired} />
                <Route path="/shows-watched" component={ShowsWatched} />
                <Route path="/countdown" component={Countdown} />
                <Route path="/episodes-to-watch" component={EpisodesToWatch} />
                <Route path="/" exact component={Main} />
                <Route path="/shows-main" component={Main} />
                <Route path="/air-dates" component={AirDates} />
                <Route path="/account" component={Account} />
                <Route path="/password" component={Password} />
                <Route path="/play-servers" component={PlayServers} />
                <Route path="/new-play-server" component={PlayServer} />
                <Route path="/play-server/:serverId" component={PlayServer} />
                <Route path="/user-shows-stats" component={UserShowsStats} />
                <Route path="/movie-new" component={MovieNew} />
                <Route path="/movie/:movieId" component={Movie} />
                <Route path="/movies-watched" component={MoviesWatched} />
                <Route path="/movies-stared" component={MoviesStared} />
            </div>
        </>
    }
}

export default Index
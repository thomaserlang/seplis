import React from 'react'
import {Route} from 'react-router-dom'

import Navbar from '../components/Navbar'
import Show from './show/Show'
import ShowNew from './show/New'
import FanOf from './FanOf'
import RecentlyAired from './RecentlyAired'
import ShowsWatched from './ShowsWatched'
import Countdown from './Countdown'
import EpisodesToWatch from './EpisodesToWatch'
import Main from './Main'
import AirDates from './AirDates'
import Account from './Account'
import Password from './Password'
import ResetPassword from './ResetPassword'
import PlayServers from './PlayServers'
import PlayServer from './PlayServer'
import UserShowsStats from './UserShowsStats'


class Index extends React.Component {

    render() {
        return <>
            <Navbar />
            <div className="container">
                <Route path="/show/:showId" component={Show} />
                <Route path="/show-new" component={ShowNew} />
                <Route path="/fan-of" component={FanOf} />
                <Route path="/recently-aired" component={RecentlyAired} />
                <Route path="/shows-watched" component={ShowsWatched} />
                <Route path="/countdown" component={Countdown} />
                <Route path="/episodes-to-watch" component={EpisodesToWatch} />
                <Route path="/" exact component={Main} />
                <Route path="/main" component={Main} />
                <Route path="/air-dates" component={AirDates} />
                <Route path="/account" component={Account} />
                <Route path="/password" component={Password} />
                <Route path="/reset-password" component={ResetPassword} />
                <Route path="/reset-password/:key" component={ResetPassword} />
                <Route path="/play-servers" component={PlayServers} />
                <Route path="/play-server" component={PlayServer} />
                <Route path="/user-shows-stats" component={UserShowsStats} />

            </div>
        </>
    }
}

export default Index
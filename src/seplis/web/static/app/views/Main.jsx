import React from 'react';
import ShowsWatched from 'components/shows/Watched';
import ShowsCountdown from 'components/shows/Countdown';
import ShowsRecentlyAired from 'components/shows/RecentlyAired';
import ShowsEpisodesToWatch from 'components/shows/EpisodesToWatch';
import {requireAuthed} from 'utils';

class Main extends React.Component {
    
    constructor(props) {
        super(props);
        requireAuthed();
    }

    render() {
        return (
            <span>
            <h2 className="header"><a href="/shows-watched">Recently watched</a></h2>    
            <div className="slider col-margin">
                <ShowsWatched perPage={6} />
            </div>

            <h2 className="header"><a href="/countdown">Countdown</a></h2>
            <div className="slider col-margin">
                <ShowsCountdown perPage={6} />
            </div>
            
            <h2 className="header"><a href="/recently-aired">Recently Aired</a></h2>
            <div className="slider col-margin">
                <ShowsRecentlyAired perPage={6} />
            </div>

            <h2 className="header"><a href="/episodes-to-watch">Episodes To Watch</a></h2>
            <div className="slider col-margin">
                <ShowsEpisodesToWatch perPage={6} />
            </div>
            </span>
        )
    }
}

export default Main;
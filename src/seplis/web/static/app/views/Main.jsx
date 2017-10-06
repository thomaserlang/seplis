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
            <h2 className="header">Recently watched</h2>    
            <div className="slider col-margin">
                <ShowsWatched perPage={6} />
            </div>

            <h2 className="header">Countdown</h2>
            <div className="slider col-margin">
                <ShowsCountdown perPage={6} />
            </div>
            
            <h2 className="header">Recently Aired</h2>
            <div className="slider col-margin">
                <ShowsRecentlyAired perPage={6} />
            </div>

            <h2 className="header">Episodes To Watch</h2>
            <div className="slider col-margin">
                <ShowsEpisodesToWatch perPage={6} />
            </div>
            </span>
        )
    }
}

export default Main;
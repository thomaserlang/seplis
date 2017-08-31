import React from 'react';
import ShowsRecentlyWatched from 'components/shows/RecentlyWatched';
import ShowsCountdown from 'components/shows/Countdown';
import ShowsRecentlyAired from 'components/shows/RecentlyAired';
import ShowsEpisodesToWatch from 'components/shows/EpisodesToWatch';

class Main extends React.Component {

    render() {
        return (
            <span>
            <h2 className="header">Recently watched</h2>    
            <div className="showlist-xscroll">
                <ShowsRecentlyWatched perPage={12} />
            </div>

            <h2 className="header">Countdown</h2>
            <div className="showlist-xscroll">
                <ShowsCountdown perPage={12} />
            </div>
            
            <h2 className="header">Recently Aired</h2>
            <div className="showlist-xscroll">
                <ShowsRecentlyAired perPage={12} />
            </div>

            <h2 className="header">Episodes To Watch</h2>
            <div className="showlist-xscroll">
                <ShowsEpisodesToWatch perPage={12} />
            </div>
            </span>
        )
    }
}

export default Main;
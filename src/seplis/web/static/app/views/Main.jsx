import React from 'react';
import ShowsRecentlyWatched from 'components/shows/RecentlyWatched';
import ShowsCountdown from 'components/shows/Countdown';
import ShowsRecentlyAiredBar from 'components/shows/RecentlyAiredBar';
import ShowsEpisodesToWatchBar from 'components/shows/EpisodesToWatchBar';

class Main extends React.Component {

    render() {
        return (
            <span>
            <ShowsRecentlyWatched />
            <ShowsCountdown />
            <ShowsRecentlyAiredBar />
            <ShowsEpisodesToWatchBar />
            </span>
        )
    }
}

export default Main;
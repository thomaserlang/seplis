import React from 'react';
import ShowsRecentlyWatched from 'components/shows/RecentlyWatched';
import ShowsCountdown from 'components/shows/Countdown';

class Main extends React.Component {

    render() {
        return (
            <span>
            <ShowsRecentlyWatched />
            <ShowsCountdown />
            </span>
        )
    }
}

export default Main;
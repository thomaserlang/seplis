import React from 'react';
import ShowsRecentlyWatched from 'components/shows/RecentlyWatched';
import ShowsAirDates from 'components/shows/AirDates';

class Main extends React.Component {

    render() {
        return (
            <span>
            <ShowsRecentlyWatched />
            </span>
        )
    }
}

export default Main;
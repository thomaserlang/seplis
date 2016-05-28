import React from 'react';

import SeasonList from 'components/shows/episodes/SeasonList';

class Seasons extends React.Component {

    render() {
        return (
            <SeasonList
                showId={this.props.show.id}
                seasons={this.props.show.seasons}
                seasonNumber={this.props.show.seasons.slice(-1)[0].season}
            />
        );
    }
}

export default Seasons;
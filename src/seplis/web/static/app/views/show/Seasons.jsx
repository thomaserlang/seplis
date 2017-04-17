import React from 'react';

import SeasonList from 'components/shows/episodes/SeasonList';

class Seasons extends React.Component {

    render() {
        let select = 0;
        if (this.props.show.seasons.length > 0)
            select = this.props.show.seasons.slice(-1)[0].season;
        return (
            <SeasonList
                showId={this.props.show.id}
                seasons={this.props.show.seasons}
                seasonNumber={select}
            />
        );
    }
}

export default Seasons;
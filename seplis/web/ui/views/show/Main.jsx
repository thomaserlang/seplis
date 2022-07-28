import React from 'react';
import PropTypes from 'prop-types';

import NextToWatch from 'components/shows/episodes/NextToWatch';
import LatestEpisodesSideBar from 'components/shows/episodes/LatestEpisodesSideBar';
import EpisodeLastWatched from 'components/shows/episodes/EpisodeLastWatched'

const propTypes = {
    show: PropTypes.object.isRequired,
}

class Main extends React.Component {

    constructor(props) {
        super(props);
    } 

    componentDidMount() {
        document.title = `${this.props.show.title} | SEPLIS`
    }

    renderAirDates() {
        if (this.props.show.status > 1) {
            return;
        }
        return (
            <div className="col-12 col-lg-4 col-margin">
                <h4 className="header">
                    Next to air
                </h4>
                <LatestEpisodesSideBar
                    showId={parseInt(this.props.show.id)}
                />
            </div>
        );
    }

    renderNextToWatch() {
        return (
            <div className="col-12 col-lg-8 col-margin">
                <div className="row">
                    <div className="col-12 col-margin">
                    <h4 className="header">
                        To watch
                    </h4>
                    <NextToWatch
                        showId={parseInt(this.props.show.id)}
                        numberOfEpisodes={2}
                    />                
                    </div>
                    <div className="col-12">
                    <h4 className="header">
                        Previously watched
                    </h4>
                    <EpisodeLastWatched showId={parseInt(this.props.show.id)} />
                    </div>
                </div>
            </div>
        )
    }

    render() {
        return (
            <div className="row">
                {this.renderNextToWatch()}
                {this.renderAirDates()}
            </div>
        )
    }
}

export default Main;
import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';

import Loader from 'components/Loader';
import FanButton from 'components/shows/FanButton';
import NextToWatchList from 'components/shows/episodes/NextToWatchList';
import LatestEpisodesSideBar from 'components/shows/episodes/LatestEpisodesSideBar';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
}

class Show extends React.Component {

    constructor(props) {
        super(props);
        this.state = {show: null};
        this.getShow();
    }

    getShow() {
        let query = {};
        if (isAuthed()) {
            query.append = 'is_fan';
        }
        request(`/1/shows/${this.props.showId}`, {
            query: query,
        }).success(show => {
            this.setState({show: show});
        });
    }

    renderShow() {
        let show = this.state.show;
        return (
            <div>
                <div className="row">
                    <div className="col-xs-12">
                        <div className="btn-fan__pull-left">
                            <FanButton showId={show.id} isFan={show.is_fan || false} />
                        </div>
                        <h1 className="hidden-xs-down">
                            {show.title}
                            &nbsp;
                            <small className="text-muted">{show.premiered.substring(0,4)}</small>
                        </h1>
                        <h1 className="hidden-sm-up small-device-header">
                            {show.title}
                            &nbsp;
                            <small className="text-muted">{show.premiered.substring(0,4)}</small>
                        </h1>
                    </div> 

                    <div className="col-xs-4 hidden-sm-up" />
                    <div className="col-xs-4 col-sm-4 col-md-4 col-margin">
                        <img 
                            src={show.poster_image.url + '@SX360'} 
                            width="100%" 
                        />
                    </div>
                    <div className="col-xs-4 hidden-sm-up" />

                    <div className="col-xs-12 col-sm-8 col-lg-5 col-margin">
                        <h4 className="header">
                            Next to watch
                        </h4>
                        <NextToWatchList
                            showId={this.props.showId}
                        />
                    </div>
                    <div className="col-xs-12 col-lg-3 col-margin">
                        <h4 className="header">
                            Air dates
                        </h4>
                        <LatestEpisodesSideBar
                            showId={this.props.showId}
                        />
                    </div>

                </div>
            </div>
        )
    }

    render() {
        if (!this.state.show) {
            return (
                <Loader />
            )
        } else {
            return this.renderShow();
        }
    }
}
Show.propTypes = propTypes;

export default Show;
import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';

import Loader from 'components/Loader';
import FanButton from 'components/shows/FanButton';

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
                        <h1>
                            {show.title}
                            &nbsp;
                            <small>{show.premiered.substring(0,4)}</small>
                        </h1>
                    </div> 

                    <div className="col-xs-4 col-sm-4 col-md-4">
                        <img src={show.poster_image.url + '@SX360'} width="100%" />
                    </div>
                    <div className="col-xs-8">
                        <div className="row">

                        </div>
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
import React from 'react';
import PropTypes from 'prop-types';
import {getUserId, dateInDays} from 'utils';
import {request} from 'api';

import './List.scss';

const propTypes = {
    perPage: PropTypes.number,
}

const defaultProps = {
    perPage: 6,
}

class Countdown extends React.Component {

    constructor(props) {
        super();
        this.state = {
            items: [],
        }
    }

    componentDidMount() {
        this.getData();
    }

    getData() {
        request(`/1/users/${getUserId()}/shows-countdown`, {
            query: {
                'per_page': this.props.perPage,
            },
        }).success(data => {
            this.setState({items: data});
        });
    }

    renderItem(item) {
        let show = item.show;
        let episode = item.episode;
        return (
            <div key={show.id} className="col-4 col-sm-3 col-md-2 col-margin">
                <div>In {dateInDays(episode.air_datetime)}</div>
                <a href={`/show/${show.id}`}>
                    <img 
                        title={show.title}
                        alt={show.title}
                        src={show.poster_image!=null?show.poster_image.url + '@SX180':''} 
                        className="img-fluid"
                    />
                </a>
            </div>
        )
    }

    render() {
        return (
            <span>
                <h2 className="header">Countdown</h2>
                <div className="row showlist-scroll">
                    {this.state.items.map(item => (
                        this.renderItem(item)
                    ))}
                </div>
            </span>
        )
    }
}
Countdown.propTypes = propTypes;
Countdown.defaultProps = defaultProps;

export default Countdown;
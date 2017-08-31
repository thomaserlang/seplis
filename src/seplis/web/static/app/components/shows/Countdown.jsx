import React from 'react';
import PropTypes from 'prop-types';
import {getUserId, dateInDays} from 'utils';
import {request} from 'api';

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

    renderShow(show, episode) {
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
            <div className="row">
                {this.state.items.map(item => (
                    this.renderShow(item.show, item.episode)
                ))}
            </div>
        )
    }
}
Countdown.propTypes = propTypes;
Countdown.defaultProps = defaultProps;

export default Countdown;
import React from 'react';
import PropTypes from 'prop-types';
import CountdownShow from './CountdownShow.jsx';
import {getUserId} from 'utils';
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

    render() {
        return (
            <span>
                <h2 className="header">Countdown</h2>
                <div className="row showlist-scroll">
                    {this.state.items.map(item => (
                        <CountdownShow 
                            key={item.show.id} 
                            show={item.show}
                            episode={item.episode}
                        />
                    ))}
                </div>
            </span>
        )
    }
}
Countdown.propTypes = propTypes;
Countdown.defaultProps = defaultProps;

export default Countdown;
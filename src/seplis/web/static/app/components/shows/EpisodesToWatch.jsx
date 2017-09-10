import React from 'react';
import PropTypes from 'prop-types';
import {getUserId, episodeTitle} from 'utils';
import {request} from 'api';

const propTypes = {
    perPage: PropTypes.number,
}

const defaultProps = {
    perPage: 6,
}

class EpisodesToWatch extends React.Component {

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
        request(`/1/users/${getUserId()}/shows-etw`, {
            query: {
                'per_page': this.props.perPage,
            },
        }).done(data => {
            this.setState({items: data});
        });
    }

    renderItem(item) {
        let show = item.show;
        let episode = item.episode;
        return (
            <div key={show.id} className="col-4 col-md-3 col-lg-2 col-margin">
                <a href={`/show/${show.id}`}>
                    <img 
                        title={show.title}
                        alt={show.title}
                        src={show.poster_image!=null?show.poster_image.url + '@SX180':''} 
                        className="img-fluid"
                    />
                </a>
                <div>{episodeTitle(show, episode)}</div>
            </div>
        )
    }

    render() {
        return (
            <div className="row">
                {this.state.items.map(item => (
                    this.renderItem(item)
                ))}
            </div>
        )
    }
}
EpisodesToWatch.propTypes = propTypes;
EpisodesToWatch.defaultProps = defaultProps;

export default EpisodesToWatch;
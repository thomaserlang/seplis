import React from 'react';
import PropTypes from 'prop-types';
import {dateInDays} from 'utils';

const propTypes = {
    show: PropTypes.object,
    episode: PropTypes.object,
}

class CountdownShow extends React.Component {
    render() {
        let show = this.props.show;
        let episode = this.props.episode;
        return (
            <div className="col-4 col-sm-3 col-md-2 col-margin">
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
}
CountdownShow.propTypes = propTypes;

export default CountdownShow;
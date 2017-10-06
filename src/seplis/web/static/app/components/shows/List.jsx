import React from 'react';
import PropTypes from 'prop-types';
import ClassNames from 'classnames';

import './List.scss';

const propTypes = {
    shows: PropTypes.array.isRequired,
    mobile_xscroll: PropTypes.bool,
}

const defaultProps = {
    mobile_xscroll: false,
}

class List extends React.Component {

    renderShow(show) {
        return (
            <div key={show.id} className="col-4 col-sm-4 col-md-3 col-lg-2 col-margin">
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
        let c = ClassNames({
            row: true,
            'slider': this.props.mobile_xscroll,
        });
        return (
            <div className={c}>
                {this.props.shows.map(show => (
                    this.renderShow(show)
                ))}
            </div>
        );
    }
}
List.propTypes = propTypes;
List.defaultProps = defaultProps;

export default List;
import React from 'react';
import PropTypes from 'prop-types';

const propTypes = {
    shows: PropTypes.array.isRequired,
    class: PropTypes.string,
}

const defaultProps = {
    class: 'col-4 col-sm-3 col-md-2 col-margin'
}

class List extends React.Component {

    renderShow(show) {
        return (
            <div key={show.id} className={this.props.class}>
                <a href={`/show/${show.id}`}>
                    <img 
                        title={show.title}
                        alt={show.title}
                        src={show.poster_image!=null?show.poster_image.url + '@SX180':''} 
                        className="img-fluid"
                    />
                </a>
                <a href={`/show/${show.id}`}>{show.title}</a>
            </div>
        )
    }

    render() {
        return (
            <div className="row">
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
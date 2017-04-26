import React from 'react';

const propTypes = {
    shows: React.PropTypes.array.isRequired,
    class: React.PropTypes.string,
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
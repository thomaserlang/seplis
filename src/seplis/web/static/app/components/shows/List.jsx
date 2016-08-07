import React from 'react';

const propTypes = {
    shows: React.PropTypes.array.isRequired,
    class: React.PropTypes.string,
}

const defaultTypes = {
    class: 'col-xs-6 col-sm-4 col-md-3 col-margin'
}

class List extends React.Component {

    renderShow(show) {
        return (
            <div key={show.id} className={this.props.class}>
                <a href={`/show/${show.id}`}>
                    <img 
                        src={show.poster_image!=null?show.poster_image.url + '@SX269':''} 
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
List.defaultTypes = defaultTypes;

export default List;
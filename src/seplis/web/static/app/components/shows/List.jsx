import React from 'react';

const propTypes = {
    shows: React.PropTypes.array.isRequired,
}

class List extends React.Component {

    renderShow(show) {
        return (
            <div key={show.id} className="col-xs-3 col-margin">
                <a href={`/show/${show.id}`}>
                    <img 
                        src={show.poster_image!=null?show.poster_image.url + '@SX360':''} 
                        width="100%" 
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

export default List;
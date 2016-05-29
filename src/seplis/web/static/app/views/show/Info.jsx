import React from 'react';


class Info extends React.Component {
    
    statusToText(status) {
        switch (status) {
            case 1: return 'Running';
            case 2: return 'Ended';
            default: return 'Unknown';
        }
    }

    renderGeneral() {
        let show = this.props.show;
        return (
            <div className="col-xs-12">
                <table className="table table-sm borderless">
                    <tbody>
                    <tr><th>Status</th><td>{this.statusToText(show.status)}</td></tr>
                    <tr><th width="100">Premiered</th><td>{show.premiered || 'unknown'}</td></tr>
                    <tr><th>Runtime</th><td>{show.runtime?show.runtime + ' minutes':'Unknown'}</td></tr>
                    <tr><th>Genres</th><td>{show.genres.join(', ')}</td></tr>
                    </tbody>
                </table>
            </div>
        )
    }

    renderDescription() {
        let desc = this.props.show.description;
        return (
            <div className="col-xs-12 col-md-12">
                <p className="text-justify">
                    {desc.text}
                    <br />
                    <font className="text-muted">Source:</font> 
                    &nbsp;<a href={desc.url} target="_blank">{desc.title}</a>
                </p>
            </div>
        )
    }

    render() {
        return (
            <div className="row">
                {this.renderGeneral()}
                
                {this.renderDescription()}
            </div>
        )
    }
}

export default Info;
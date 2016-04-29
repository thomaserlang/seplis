import React from 'react';

const propTypes = {
    seasons: React.PropTypes.array.isRequired,
    selectedEpisodeNumber: React.PropTypes.number,
    onChange: React.PropTypes.func,
    name: React.PropTypes.string,
}

class SelectSeasonEpisode extends React.Component {

    renderSeason(item) {
        let rows = [];
        for (let i = item.from; i <= item.to; i++) {
            rows.push(
                <option key={i} value={i}>
                    S{item.season}: Episode {i-item.from+1}
                </option>
            )
        }
        return (
            <optgroup key={item.season} label={`Season ${item.season}`}>
                {rows}
            </optgroup>
        )
    }

    render() {
        return (
            <select 
                name={this.props.name}
                className="form-control"
                onChange={this.props.onChange}
            >
                {this.props.seasons.map((item, index) => (
                    this.renderSeason(item)
                ))}
            </select>
        )
    }
}
SelectSeasonEpisode.propTypes = propTypes;

export default SelectSeasonEpisode;
import React from 'react';
import PropTypes from 'prop-types';

const propTypes = {
    seasons: PropTypes.array.isRequired,
    selectedSeason: PropTypes.number,
    onChange: PropTypes.func,
}

class SelectSeason extends React.Component {

    render() {
        return (
            <select 
                className="form-control" 
                value={this.props.selectedSeason}
                onChange={this.props.onChange}
            >
                {this.props.seasons.map((item, key) => (
                    <option 
                        key={item.season}
                        value={item.season}
                    >
                        Season {item.season}
                    </option>
                ))}
            </select>
        )
    }

}
SelectSeason.propTypes = propTypes;

export default SelectSeason;
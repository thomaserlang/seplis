import React from 'react';
import SelectSeasonEpisode from './SelectSeasonEpisode';
import {request} from 'utils';

import 'bootstrap/js/dropdown';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
    seasons: React.PropTypes.array.isRequired,
}

class WatchedProgression extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showForm: false,
            fromNumber: 1,
            toNumber: 1,
        }
        this.dropdownButtonClick = this.dropdownButtonClick.bind(this);
        this.selectChange = this.selectChange.bind(this);
    }

    selectChange(e) {
        this.state[e.target.name] = parseInt(e.target.value);
        if (this.state.fromNumber > this.state.toNumber)
            this.state.toNumber = this.state.fromNumber;
        this.setState(this.state);
    }

    dropdownButtonClick(e) {
        this.setState({showForm: true});
    }

    getUserWatching() {
        request('/')
    }

    renderForm() {
        return (
            <form>
                <div className="form-group">                    
                    <label>From episode</label>
                    <SelectSeasonEpisode
                        seasons={this.props.seasons}
                        name="fromNumber"
                        onChange={this.selectChange}
                        selectedNumber={this.state.fromNumber}
                    />
                </div>
                <div className="form-group">
                    <label>To episode</label>
                    <SelectSeasonEpisode
                        seasons={this.props.seasons}
                        name="toNumber"
                        onChange={this.selectChange}
                        selectedNumber={this.state.toNumber}
                    />
                </div>
                <button type="submit" className="btn btn-primary">
                    Watched
                </button>
            </form>
        )
    }

    render() {
        return (
            <div className="dropdown">
                <button 
                    className="btn btn-dark btn-transparent" 
                    data-toggle="dropdown"
                    onClick={this.dropdownButtonClick}
                >
                    Set progression
                </button>
                <div className="dropdown-menu">                    
                    {this.state.showForm?this.renderForm():''}
                </div>
            </div>
        )
    }

}
WatchedProgression.propTypes = propTypes;

export default WatchedProgression;
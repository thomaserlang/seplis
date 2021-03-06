import React from 'react';
import PropTypes from 'prop-types';
import SelectSeasonEpisode from './SelectSeasonEpisode';
import {request} from 'api';
import {getUserId} from 'utils';

import 'popper.js';
import 'bootstrap/js/src/dropdown';
import './WatchedProgression.scss';

const propTypes = {
    showId: PropTypes.number.isRequired,
    seasons: PropTypes.array.isRequired,
}

class WatchedProgression extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showForm: false,
            fromNumber: 1,
            toNumber: 1,
            saving: false,
        }
        this.dropdownButtonClick = this.dropdownButtonClick.bind(this);
        this.selectChange = this.selectChange.bind(this);
        this.formSubmit = this.formSubmit.bind(this);
    }

    selectChange(e) {
        this.state[e.target.name] = parseInt(e.target.value);
        if (this.state.fromNumber > this.state.toNumber)
            this.state.toNumber = this.state.fromNumber;
        this.setState(this.state);
    }

    dropdownButtonClick(e) {
        this.getNextToWatch();
    }

    getNextToWatch() {
        request(
            `/1/shows/${this.props.showId}/episodes/to-watch`
        ).done(episode => {
            if (this.state.showForm === false)
                // Render the form and it's options before 
                // setting the selected value. Otherwise it will not work.
                this.setState({showForm:true});
            this.setState({
                fromNumber: episode.number,
                toNumber: episode.number,
            });
        }).fail(error => {
            if (error.responseJSON.code === 1301) {
                this.setState({showForm:true});
            }
        });
    }

    formSubmit(e) {
        e.preventDefault();
        this.setState({'saving': true})
        let id = this.props.showId;
        let fromN = this.state.fromNumber;
        let toN = this.state.toNumber;
        request(
            `/1/shows/${id}/episodes/${fromN}-${toN}/watched`,
            {method: 'PUT'}
        ).fail(() => {
            this.setState({'saving': false});
        }).done(() => {
            location.reload();
        });
    }

    renderForm() {
        return (
            <form onSubmit={this.formSubmit}>
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
                <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={this.state.saving}
                >
                    {this.state.saving?'Please wait...':'Watched'}
                </button>
            </form>
        )
    }

    render() {
        return (
            <div className="dropdown watched-progression">
                <button 
                    className="btn btn-dark btn-transparent dropdown-toggle" 
                    data-toggle="dropdown"
                    onClick={this.dropdownButtonClick}
                >
                    Set progression
                </button>
                <div className="dropdown-menu dropdown-menu-right">                    
                    {this.state.showForm?this.renderForm():''}
                </div>
            </div>
        )
    }

}
WatchedProgression.propTypes = propTypes;

export default WatchedProgression;
import React from 'react';
import ClassNames from 'classnames';
import {getUserId} from 'utils';
import {request} from 'api';

import './FanButton.scss';

const propTypes = {
    showId: React.PropTypes.number.isRequired,
    isFan: React.PropTypes.bool.isRequired,
}

class FanButton extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            isFan: props.isFan,
        }
        this.onClick = this.onClick.bind(this);
    }

    onClick(e) {
        e.preventDefault();
        this.setState({isFan: !this.state.isFan});
        request(`/1/shows/${this.props.showId}/fans/${getUserId()}`, {
            method: this.state.isFan?'DELETE':'PUT',
        }).error(() => {            
            this.setState({isFan: !this.state.isFan});
        })
    }

    render() {
        let btnClass = ClassNames({
            btn: true,
            'btn-fan': true,
            'btn-fan__is-fan': this.state.isFan, 
        });
        return (
            <button 
                className={btnClass}
                onClick={this.onClick}
            >
                {this.state.isFan?'Fan':'Become a Fan'}
            </button>
        );
    }
}
FanButton.propTypes = propTypes;

export default FanButton;
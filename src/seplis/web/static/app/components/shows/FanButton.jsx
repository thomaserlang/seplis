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
        request(`/1/users/${getUserId()}/fan-of/${this.props.showId}`, {
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
                title={this.state.isFan?'Unfan':'Become a Fan'}
                aria-label={this.state.isFan?'Unfan':'Become a Fan'}                
            >
                {this.state.isFan?
                    <span className="fa fa-star"></span>
                    :
                    <span className="fa fa-star-o"></span>
                }
            </button>
        );
    }
}
FanButton.propTypes = propTypes;

export default FanButton;
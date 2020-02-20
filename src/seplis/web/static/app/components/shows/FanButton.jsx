import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {isAuthed,getUserId} from 'utils'
import {request} from 'api'

import './FanButton.scss'

const propTypes = {
    showId: PropTypes.number.isRequired,
    isFan: PropTypes.bool,
}

class FanButton extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            isFan: props.isFan,
        }
        this.onClick = this.onClick.bind(this)
    }

    componentDidMount() {
        if (this.props.isFan == undefined)
            this.getIsFan()
    }

    onClick(e) {
        e.target.blur()
        e.preventDefault()
        this.setState({isFan: !this.state.isFan})
        request(`/1/users/${getUserId()}/fan-of/${this.props.showId}`, {
            method: this.state.isFan?'DELETE':'PUT',
        }).fail(() => {            
            this.setState({isFan: !this.state.isFan})
        })
    }

    getIsFan() {
        if (!isAuthed()) 
            return
        request(
            `/1/users/${getUserId()}/fan-of/${parseInt(this.props.showId)}`
        ).done(d => {
            this.setState({isFan: d.is_fan})
        })
    }

    render() {
        let btnClass = ClassNames({
            btn: true,
            'btn-fan': true,
            'btn-fan__is-fan': this.state.isFan, 
        })
        return (
            <button 
                className={btnClass}
                onClick={this.onClick}
                title={this.state.isFan?'Unfollow':'Follow'}
                aria-label={this.state.isFan?'Unfollow':'Follow'}                
            >
                {this.state.isFan?
                    'Following'
                    :
                    'Follow'
                }
            </button>
        )
    }
}
FanButton.propTypes = propTypes

export default FanButton
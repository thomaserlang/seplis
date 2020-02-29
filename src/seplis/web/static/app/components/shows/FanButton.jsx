import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {isAuthed,getUserId} from 'utils'
import {request} from 'api'

import './FanButton.scss'

const propTypes = {
    showId: PropTypes.number.isRequired,
    following: PropTypes.bool,
}

class FanButton extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            following: props.following,
        }
        this.onClick = this.onClick.bind(this)
    }

    componentDidMount() {
        if (this.props.following == undefined)
            this.get()
    }

    onClick(e) {
        e.target.blur()
        e.preventDefault()
        this.setState({following: !this.state.following})
        request(`/1/users/${getUserId()}/shows-following/${this.props.showId}`, {
            method: this.state.following?'DELETE':'PUT',
        }).fail(() => {            
            this.setState({following: !this.state.following})
        })
    }

    get() {
        if (!isAuthed()) 
            return
        request(
            `/1/users/${getUserId()}/shows-following/${parseInt(this.props.showId)}`
        ).done(d => {
            this.setState({following: d.following})
        })
    }

    render() {
        let btnClass = ClassNames({
            btn: true,
            'btn-fan': true,
            'btn-fan__is-fan': this.state.following, 
        })
        return (
            <button 
                className={btnClass}
                onClick={this.onClick}
                title={this.state.following?'Unfollow':'Follow'}
                aria-label={this.state.following?'Unfollow':'Follow'}                
            >
                {this.state.following?
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
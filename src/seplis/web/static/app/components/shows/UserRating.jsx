import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {isAuthed,getUserId} from 'utils'
import {request} from 'api'

const propTypes = {
    showId: PropTypes.number.isRequired,
    rating: PropTypes.number,
}

class UserRating extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            rating: props.rating,
        }
    }

    componentDidMount() {
        if (this.props.rating == undefined)
            this.getRating()
    }

    handleChange = (e) => {
        e.preventDefault()
        e.target.blur()
        if (e.target.value == '') {
            this.setState({rating: ''})
            request(`/1/shows/${this.props.showId}/user-rating`, {
                method: 'DELETE',
            })
        } else {
            let s = parseInt(e.target.value)
            this.setState({rating: s})
            request(`/1/shows/${this.props.showId}/user-rating`, {
                data: {
                    rating: s,
                },
                method: 'PUT',
            })
        }
    }

    getRating() {
        if (!isAuthed()) 
            return
        request(
            `/1/shows/${this.props.showId}/user-rating`
        ).done(d => {
            this.setState({rating: d.rating?d.rating:''})
        })
    }

    render() {
        return (
            <select 
                className="form-control dark-input"
                value={this.state.rating} 
                onChange={this.handleChange}
                style={{width:'auto', textAlignLast: 'right'}}
            >                
                {Array(10).fill(1).map((e, i) =>
                    <option key={`user-rating-${11-(i+1)}`} value={11-(i+1)}>{11-(i+1)}/10</option>
                )}
                <option value="">★ Not rated</option>
            </select>
        )
    }
}
UserRating.propTypes = propTypes

export default UserRating
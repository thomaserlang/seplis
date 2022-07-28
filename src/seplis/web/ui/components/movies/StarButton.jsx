import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {isAuthed} from 'utils'
import {request} from 'api'

import './StarButton.scss'

const propTypes = {
    movieId: PropTypes.number.isRequired,
    stared: PropTypes.bool,
}

class StarButton extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            stared: props.stared,
        }
        this.onClick = this.onClick.bind(this)
    }

    componentDidMount() {
        if (this.props.stared == undefined)
            this.get()
    }

    onClick(e) {
        e.target.blur()
        e.preventDefault()
        this.setState({stared: !this.state.stared})
        request(`/1/movies/${this.props.movieId}/stared`, {
            method: this.state.stared?'DELETE':'PUT',
        }).fail(() => {            
            this.setState({stared: !this.state.stared})
        })
    }

    get() {
        if (!isAuthed()) 
            return
        request(
            `/1/movies/${parseInt(this.props.movieId)}/stared`
        ).done(d => {
            this.setState({stared: d.stared})
        })
    }

    render() {
        let btnClass = ClassNames({
            btn: true,
            'btn-star': true,
            'btn-star__is-stared': this.state.stared, 
        })
        return (
            <button 
                className={btnClass}
                onClick={this.onClick}
                title={this.state.stared?'Unstar':'Star'}
                aria-label={this.state.stared?'Unstar':'Star'}                
            >
                {this.state.stared?'★':'☆'}
            </button>
        )
    }
}
StarButton.propTypes = propTypes

export default StarButton
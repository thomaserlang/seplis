import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'
import {request} from 'api'

const propTypes = {
    onChange: PropTypes.func,
    selected: PropTypes.string,
}

class SelectGenres extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            genres: [],
            selectedGenre: props.selected,
        }
    }

    componentDidMount() {
        this.load()
    }

    load() {
        request(`/1/show-genres`).done((d) => {
            this.setState({genres:d})
        })
    }

    onChange = (e) => {
        e.target.blur()
        let t = e.target.value
        this.setState({
            selectedGenre: t,
        })
        if (this.props.onChange != undefined) 
            this.props.onChange(t)
    }

    render() {
        return <select 
            className="form-control" 
            value={this.state.selectedGenre}
            onChange={this.onChange}
        >
            <option value="">Genres</option>
            {this.state.genres.map((g, i) => (
                <option key={`genre-${i}`} value={g}>{g}</option>
            ))}
        </select>
    }
}
SelectGenres.propTypes = propTypes

export default SelectGenres

                        
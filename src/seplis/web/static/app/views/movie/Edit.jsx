import React from 'react'
import PropTypes from 'prop-types'
import EditFields from 'components/movies/EditFields'
import Serialize from 'form-serialize'
import {unflatten} from 'flat'
import {request} from 'api'
import {getUserLevel} from 'utils';

const propTypes = {
    movie: PropTypes.object,
}

class Edit extends React.Component {

    constructor(props) {
        super(props)
        this.onSubmit = this.submit.bind(this)
        this.state = {
            error: null,
            success: null,
            loading: false,
            deleting: false,
            deleteSuccess: null,
        }
    }

    componentDidMount() {
        document.title = `${this.props.movie.title} - Edit Movie | SEPLIS`
    }

    submit(e) {
        e.preventDefault()
        this.setState({
            success: null,
            error: null,
            loading: true,
        })
        let data = unflatten(
            Serialize(e.target, {hash: true})
        )
        request(`/1/movies/${this.props.movie.id}`, {
            data: data,
            method: 'PATCH',
        }).done(movie => {
            this.setState({success: movie})
            request(`/1/movies/${this.props.movie.id}/update`, {
                method: 'POST',
            })
        }).fail(e => {
            this.setState({error: e.responseJSON})
        }).always(() => {
            this.setState({loading: false})
        })
    }

    renderError() {
        if (!this.state.error) 
            return
        return (
            <div className="alert alert-danger">
                {this.state.error.message}
            </div>
        )
    }

    renderSuccess() {
        if (!this.state.success) 
            return
        return (
            <div className="alert alert-success">
                The movie was successfully updated.
            </div>
        )
    }

    deleteClick = (e) => {
        e.preventDefault()
        if (!confirm('Sure you want to delete this movie?'))
            return
        this.setState({deleting: true})
        request(`/1/movies/${this.props.movie.id}`, {
            method: 'DELETE',
        }).done(() => {
            location.href = '/'
        }).fail(e => {
            this.setState({error: e.responseJSON})
        }).always(() => {
            this.setState({deleting: false})
        })
    }

    renderDelete() {
        if (getUserLevel() < 3)
            return
        return <button 
            className="btn btn-warning mr-2"
            disabled={this.state.deleting}
            onClick={this.deleteClick}
        >
            {this.state.deleting?'Deleting...':'Delete'}
        </button>
    }

    render() {
        return (
            <form method="post" onSubmit={this.onSubmit}>
                <EditFields movie={this.props.movie} />
                {this.renderError()}
                {this.renderSuccess()}
                {this.renderDelete()}
                <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={this.state.loading}
                >
                    {this.state.loading?'Saving...':'Save'}
                </button>
            </form>
        )
    }
}
Edit.propTypes = propTypes

export default Edit
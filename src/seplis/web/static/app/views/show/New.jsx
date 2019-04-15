import React from 'react'
import {Link} from 'react-router-dom'
import EditFields from 'components/shows/EditFields'
import Serialize from 'form-serialize'
import {unflatten} from 'flat'
import {request} from 'api'

class New extends React.Component {

    constructor(props) {
        super(props)
        this.onSubmit = this.submit.bind(this)
        this.state = {
            success: null,
            error: null,
            loading: false,
        }
    }
    
    componentDidMount() {
        document.title = `New Show | SEPLIS`
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
        request('/1/shows', {
            data: data,
            method: 'POST',
        }).done(show => {
            this.setState({success: show})
        }).fail(e => {
            this.setState({error: e.responseJSON})
        }).always(() => {
            this.setState({loading: false})
        })
    }

    renderError() {
        if (!this.state.error) return ''
        switch (this.state.error.code) {
            case 1403:
                let title = this.state.error.extra.show.title || 'the show'
                return (
                    <div className="alert alert-danger">
                        {this.state.error.message}.<br />
                        <a href={`/show/${this.state.error.extra.show.id}`}>
                            Go to {title}
                        </a>.
                    </div>
                )
               break
            default: 
                return (
                    <div className="alert alert-danger">
                        {this.state.error.message}
                    </div>
                )
                break
        }
    }

    renderSuccess() {
        return (
            <span>
            <h1>Show successfully created</h1>
            <div className="alert alert-success">
                The show has been created. It will be imported shortly.
                <ul>
                    <li><a href={`/show/${this.state.success.id}`}>Go to the show</a></li>
                    <li><Link to="/show-new">Create another show</Link></li>
                </ul>
            </div>
            </span>
        )        
    }

    render() {
        if (this.state.success != null)
            return this.renderSuccess()

        return (
            <form method="post" onSubmit={this.onSubmit}>
                <h1>New show</h1>
                <EditFields />
                {this.renderError()}
                <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={this.state.loading}
                >
                    {this.state.loading?'Creating...':'Create'}
                </button>
            </form>
        )
    }
}

export default New
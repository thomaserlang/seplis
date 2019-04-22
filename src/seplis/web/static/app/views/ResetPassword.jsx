import React from 'react'
import {Link} from 'react-router-dom'
import RenderError from 'components/RenderError'
import {request} from 'api'

class ResetPassword extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            error: null,
            success: null,
            loading: false,
        }
        this.submitEmail = this.submitEmail.bind(this)
        this.submitReset = this.submitReset.bind(this)
    }

    componentDidMount() {
        document.title = `Reset Password | SEPLIS`
    }

    submitEmail(e) {
        e.preventDefault()
        this.setState({success: false, loading: true, error: null})
        request('/1/user-reset-password', {
            query: {
                'email': this.email.value,
            }
        }).fail(e => {
            this.setState({error: e.responseJSON, loading: false})
        }).done(() => {
            this.setState({success: true, loading: false})
        })
    }

    submitReset(e) {
        e.preventDefault()
        this.setState({success: false, loading: true, error: null})
        request('/1/user-reset-password', {
            data: {
                'key': this.props.match.params.key,
                'new_password': this.password.value
            }
        }).fail(e => {
            this.setState({error: e.responseJSON, loading: false})
        }).done(() => {
            this.setState({success: true, loading: false})
        })
    }

    renderSendSuccess() {
        if (!this.state.success) return
        return (
            <div className="alert alert-success">
                <strong>A reset link has been sent to your email.</strong>
            </div>
        )
    }

    renderButton() {
        if (this.state.loading == false)
            return (
                <button type="submit" className="btn btn-primary ml-auto">Submit</button>
            )
        if (this.state.loading == true) 
            return (
                <button type="submit" className="btn btn-primary ml-auto" disabled={true}>
                    Working...
                </button>
            )        
    }

    renderSendForm() {
        if (this.state.success)
            return
        return <form onSubmit={this.submitEmail}>
            <label>Email</label>
            <input 
                ref={(ref) => (this.email = ref)}
                type="email"
                name="email"
                className="form-control dark-form-control mb-4"
                required={true}
                autoFocus={true}
            />
            <div className="d-flex">
                <Link className="btn" to="/sign-in">Sign in</Link>
                {this.renderButton()}
            </div>
        </form>
    }

    renderSend() {
        return <div className="standard-form">
            <div className="logo">SEPLIS</div>
            <div className="title">Reset password</div>
            <RenderError error={this.state.error} />
            {this.renderSendForm()}
            {this.renderSendSuccess()}
        </div>
    }

    renderResetSuccess() {
        if (!this.state.success) return
        return (
            <div className="alert alert-success">
                Your password has been changed. Sign in <Link to="/sign-in">here</Link>.
            </div>
        )
    }

    renderResetForm() {
        if (this.state.success)
            return
        return <form onSubmit={this.submitReset}>
            <label>New password</label>
            <input 
                ref={(ref) => (this.password = ref)}
                type="password"
                name="password"
                className="form-control dark-form-control mb-4"
                required={true}
                autoFocus={true}
            />
            <div className="d-flex">
                {this.renderButton()}
            </div>
        </form>
    }

    renderReset() {
        return <div className="standard-form">
            <div className="logo">SEPLIS</div>
            <div className="title">Reset password</div>
            <RenderError error={this.state.error} />
            {this.renderResetForm()}
            {this.renderResetSuccess()}
        </div>
    }

    render() {
        if (this.props.match.params.key)
            return this.renderReset()
        return this.renderSend()
    }

}

export default ResetPassword
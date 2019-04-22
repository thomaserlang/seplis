import React from 'react'
import {Link} from 'react-router-dom'
import {request} from 'api'

import 'styles/StandardForm.scss'

class SignIn extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            error: '',
            email: '',
            password: '',
        }
        this.onSignIn = this.onSignIn.bind(this)
        this.onDataChange = this.onDataChange.bind(this)
    }    

    componentDidMount() {
        document.title = `Sign In | SEPLIS`
    }

    onSignIn(e) {
        e.preventDefault()
        request('/1/token', {
            data: {
                client_id: seplisClientId,
                grant_type: 'password',
                email: this.state.email,
                password: this.state.password,
            }
        }).fail(e => {
            this.setState({
                error: e.responseJSON.message,
                password: '',
            })
        }).done(data => {
            localStorage.setItem('access_token', data.access_token)
            this.saveUserIdAndRedirect()
        })
    }

    saveUserIdAndRedirect() {
        request('/1/users/current').done(user => {
            localStorage.setItem('user_id', user.id)
            localStorage.setItem('user_level', user.level)
            location.href = '/'
        })
    }

    onDataChange(e) {
        this.state[e.target.name] = e.target.value
        this.setState({error:''})
    }

    renderForm() {
        return (
            <form onSubmit={this.onSignIn}>
                <div className="form-group">
                    <input 
                        name="email"
                        type="text"
                        className="form-control dark-form-control" 
                        placeholder="Email or username"
                        onChange={this.onDataChange}
                        value={this.state.email}
                        autoFocus
                        required
                    />
                </div>
                <div className="form-group">
                    <input
                        name="password"
                        type="password"
                        className="form-control dark-form-control" 
                        placeholder="Password"
                        onChange={this.onDataChange}
                        value={this.state.password}
                        required
                    />
                </div>
                <div className="d-flex">
                    <Link className="btn" to="/reset-password">Reset password</Link>
                    <button 
                        type="submit" 
                        className="btn btn-primary ml-auto"
                    >
                        Sign in
                    </button>
                </div>
            </form>
        )
    }

    renderError() {
        if (!this.state.error) return
        return (
            <div 
                className="alert alert-warning capitalize-first-letter" 
                role="alert"
            >
                <strong>{this.state.error}</strong>
            </div>
        )
    }

    render() {
        return (
            <div className="standard-form">
                <div className="logo">SEPLIS</div>
                <div className="title">Sign in</div>
                {this.renderError()}
                {this.renderForm()}
            </div>            
        )
    }
}

export default SignIn
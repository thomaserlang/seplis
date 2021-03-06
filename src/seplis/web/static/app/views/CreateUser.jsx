import React from 'react'
import {Link} from 'react-router-dom'
import {request} from 'api'
import {withRouter} from 'react-router'

import 'styles/StandardForm.scss'

class CreateUser extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            error: null,
        }
        this.onSubmit = this.onSubmit.bind(this)
    }

    componentDidMount() {
        document.title = `Create User | SEPLIS`
    }

    onSubmit(e) {
        e.preventDefault()
        this.setState({
            error: null,
        })
        var email = e.target.email.value
        var password = e.target.password.value
        request('/1/users', {
            data: {
                name: e.target.name.value,
                email: email,
                password: password,
            }
        }).fail(e => {
            this.setState({
                error: e.responseJSON,
            })
        }).done(data => {
            localStorage.setItem('user_id', data.id)
            localStorage.setItem('user_level', data.level)
            this.signin(email, password)
        })
    }

    signin(email, password) {
        request('/1/token', {
            data: {
                client_id: seplisClientId,
                grant_type: 'password',
                email: email,
                password: password,
            }
        }).fail(e => {
            this.setState({
                error: e.responseJSON,
            })
        }).done(data => {
            localStorage.setItem('access_token', data.access_token)
            location.href = '/'
        })
    }

    renderForm() {
        return (
            <form onSubmit={this.onSubmit}>
                <div className="form-group">
                    <label>Username</label>
                    {this.renderFieldError('name')}
                    <input 
                        name="name"
                        type="text"
                        className="form-control dark-form-control"
                        autoFocus
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Email</label>
                    {this.renderFieldError('email')}
                    <input 
                        name="email"
                        type="text"
                        className="form-control dark-form-control" 
                        placeholder=""
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Password</label>
                    {this.renderFieldError('password')}
                    <input
                        name="password"
                        type="password"
                        className="form-control dark-form-control" 
                        placeholder="Minimum 6 chars"
                        required
                    />
                </div>
                <div className="d-flex">
                    <Link className="btn" to="/sign-in">Sign in</Link>
                    <button 
                        type="submit" 
                        className="btn btn-primary ml-auto"
                    >
                        Create user
                    </button>
                </div>
            </form>
        )
    }

    renderError() {
        if (!this.state.error) return
        return (
            <div className="alert alert-warning capitalize-first-letter">
                <strong>{this.state.error.message}</strong>
            </div>
        )
    }

    renderFieldError(field) {
        if ((!this.state.error) || ((!this.state.error.errors))) return
        for (let error of this.state.error.errors) {
            if (error.field == field) {
                return (
                    <p className="text-danger">{error.message}</p>
                )
            }
        }
    }

    render() {
        return (
            <div className="standard-form">
                <div className="logo">SEPLIS</div>
                <div className="title">Create user</div>
                {this.renderError()}
                {this.renderForm()}
            </div>            
        )
    }
}

export default withRouter(CreateUser)
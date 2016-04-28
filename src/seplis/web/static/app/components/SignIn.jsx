import React from 'react';
import $ from 'jquery';
import {request, apiClientSettings} from 'api';

import 'styles/StandardForm.scss';

class SignIn extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            error: '',
            email: '',
            password: '',
        }
        this.onSignIn = this.onSignIn.bind(this);
        this.onDataChange = this.onDataChange.bind(this);
    }

    onSignIn(e) {
        e.preventDefault();
        request('/1/token', {
            data: {
                client_id: apiClientSettings.clientId,
                grant_type: 'password',
                email: this.state.email,
                password: this.state.password,
            }
        }).error(e => {
            this.setState({
                error: e.responseJSON.message,
                password: '',
            });
        }).success(data => {
            localStorage.setItem('access_token', data.access_token);
            location.href = '/';
        });
    }

    onDataChange(e) {
        this.state[e.target.name] = e.target.value;
        this.setState({error:''});
    }

    renderForm() {
        return (
            <form onSubmit={this.onSignIn}>
                <div className="form-group">
                    <input 
                        name="email"
                        type="text"
                        className="form-control dark-form-control" 
                        placeholder="Email/username"
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
                <a className="btn" href="/sign-up">Create user</a>
                <button 
                    type="submit" 
                    className="btn btn-primary pull-right"
                >
                    Sign in
                </button>
            </form>
        )
    }

    renderError() {
        if (!this.state.error) return;
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

export default SignIn;
import React from 'react';
import {requireAuthed} from 'utils';
import {request} from 'api';


class Password extends React.Component {

    constructor(props) {
        super(props);
        requireAuthed();
        this.state = {
            error: null,
            success: null,
            loading: false,
        }
        this.onSubmit = this.onSubmit.bind(this);
    }

    onSubmit(e) {
        e.preventDefault();
        this.setState({error:null, success: null, loading: true});
        request('/1/users/current/change-password', {
            data: {
                'password': this.password.value,
                'new_password': this.newPassword.value,
            }
        }).error(e => {
            this.password.focus();
            this.setState({error: e.responseJSON, loading: false});
        }).success(() => {
            this.setState({success: true, loading: false});
        }).always(() => {            
            this.password.value = '';
            this.newPassword.value = '';
        });
    }

    renderError() {
        if (!this.state.error) return;
        return (
            <div className="alert alert-warning capitalize-first-letter">
                <strong>{this.state.error.message}</strong>
            </div>
        )
    }

    renderFieldError(field) {
        if ((!this.state.error) || ((!this.state.error.errors))) return;
        for (let error of this.state.error.errors) {
            if (error.field == field) {
                return (
                    <p className="text-danger">{error.message}</p>
                )
            }
        }
    }

    renderSuccess() {
        if (!this.state.success) return;
        return (
            <div className="alert alert-success">
                <strong>Your password was successfully changed.</strong>
            </div>
        )
    }

    renderButton() {
        if (this.state.loading == false)
            return (
                <button type="submit" className="btn btn-primary">Save</button>
            );
        if (this.state.loading == true) 
            return (
                <button type="submit" className="btn btn-primary" disabled={true}>
                    Changing your password...
                </button>
            );        
    }

    render() {
        return (
            <div className="row">
                <div className="col-xs-12">
                    <h1 className="col-margin">Change password</h1>
                </div>
                <div className="col-xs-12 col-sm-8 col-md-6">
                    {this.renderSuccess()}
                    {this.renderError()}
                    <form method="post" onSubmit={this.onSubmit}>
                        <div className="form-group">
                            <label>Current password</label>
                            {this.renderFieldError('password')}
                            <input 
                                ref={(ref) => (this.password = ref)}
                                type="password"
                                name="password"
                                className="form-control dark-form-control" 
                            />
                        </div>                        
                        <div className="form-group">
                            <label>New password</label>
                            {this.renderFieldError('new_password')}
                            <input 
                                ref={(ref) => (this.newPassword = ref)}
                                type="password"
                                name="new_password"
                                className="form-control dark-form-control"
                            />
                        </div>
                        {this.renderButton()}
                    </form>
                </div>
            </div>
        )
    }
}

export default Password;
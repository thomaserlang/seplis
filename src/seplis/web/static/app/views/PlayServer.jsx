import React from 'react';
import PropTypes from 'prop-types';
import {withRouter} from 'react-router';
import Loader from 'components/Loader';
import {requireAuthed, getUserId} from 'utils';
import {request} from 'api';

const propTypes = {
    location: PropTypes.object.isRequired,
}

class PlayServer extends React.Component {

    constructor(props) {
        super(props);
        requireAuthed();
        this.onSubmit = this.onSubmit.bind(this);
        this.onDelete = this.onDelete.bind(this);
        this.onGiveAccess = this.onGiveAccess.bind(this);
        this.onRemoveUserAccess = this.onRemoveUserAccess.bind(this);
        this.state = {
            loading: 0,
            error: null,
            success: false,
            playServer: {
                name: '',
                url: '',
                secret: '',
            },
            users: [],
        }
    }

    componentDidMount() {
        if (this.props.location.query.id) {
            this.getPlayServer();
            this.getUsersWithAccess();
        }
    }

    incLoading(val) {
        this.setState((state) => {
            return {loading: state.loading + val}
        })
    }

    getPlayServer() {
        this.incLoading(1);
        request(
            `/1/users/${getUserId()}/play-servers/${this.props.location.query.id}`
        ).fail(e => {
            // TODO: display the error...
        }).done(data => {
            this.setState({playServer: data});
        }).always(() => {
            this.incLoading(-1);
        });
    }

    getUsersWithAccess() {
        this.incLoading(1);
        request(
            `/1/users/${getUserId()}/play-servers/${this.props.location.query.id}/users`
        ).fail(e => {
            // TODO: display the error...
        }).done(data => {
            this.setState({users: data});
        }).always(() => {
            this.incLoading(-1);
        });
    }

    onSubmit(e) {
        e.preventDefault();
        let url = `/1/users/${getUserId()}/play-servers`;
        if (this.props.location.query.id) {
            url += `/${this.props.location.query.id}`;
        }
        request(url, {
            method: this.props.location.query.id?'PUT':'POST',
            data: {
                name: this.name.value,
                url: this.url.value,
                secret: this.secret.value,
            }
        }).fail(e => {
            this.setState({error: e.responseJSON});
        }).done(data => {
            this.props.router.push(`/play-server?id=${data.id}`);
        });
    }

    onDelete(e) {
        e.preventDefault();
        if (!confirm('Are you sure you wan\'t to delete this play server?'))
            return;
        request(`/1/users/${getUserId()}/play-servers/${this.props.location.query.id}`, {
            method: 'DELETE',
        }).fail(e => {
            this.setState({error: e.responseJSON});
        }).done(() => {
            this.props.router.push('/play-servers');
        });
    }

    onGiveAccess(e) {
        e.preventDefault();
        var value = e.target.name.value;
        request('/1/users', {
            query: {
                q: value,
            }
        }).fail(e => {
            alert(e.message);
        }).done(data => {
            if (data.length != 1) {
                alert(`Unknown user: ${value}`);
                return;
            }
            let id = this.props.location.query.id;
            request(`/1/users/${getUserId()}/play-servers/${id}/users/${data[0].id}`, {
               method: 'PUT',
            }).fail(e => {
                alert(e.message);
            }).done(() => {
                this.getUsersWithAccess();
            });
        });
    }

    onRemoveUserAccess(e) {
        e.preventDefault();
        let id = this.props.location.query.id;
        request(`/1/users/${getUserId()}/play-servers/${id}/users/${e.target.userId.value}`, {
           method: 'DELETE',
        }).fail(e => {
            alert(e.message);
        }).done(() => {
            this.getUsersWithAccess();
        });
    }

    renderUsers() {
        if (this.state.users.length == 0)
            return (
                <div className="alert alert-info">
                    No one has access to this play server. 
                </div>
            );
        return (
            <table className="table">
                <tbody>
                    {this.state.users.map(u => (
                        <tr key={u.id}>
                            <td>{u.name}</td>
                            <td width="10px" className="text-xs-right">
                                <form onSubmit={this.onRemoveUserAccess}>
                                    <input 
                                        type="hidden"
                                        name="userId"
                                        value={u.id}
                                    />
                                    <button type="submit" className="btn-link">
                                        <i className="fa fa-times"></i>
                                    </button>
                                </form>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        )
    }

    renderGiveAccessForm() {
        return (
            <form className="col-margin row" onSubmit={this.onGiveAccess}>
                <div className="col-6">
                <input 
                    type="text"
                    name="name"
                    className="form-control dark-form-control" 
                    placeholder="Username"
                />
                </div>
                <div className="col-4">
                <button className="btn btn-success">
                    Give access
                </button>
                </div>
            </form>
        )
    }

    renderUsersWithAccess() {
        if (!this.props.location.query.id) return;
        return (
            <span>
                <h2 className="col-margin">Users with access</h2>
                {this.renderGiveAccessForm()}
                {this.renderUsers()}
            </span>
        )
    }

    renderDeleteButton() {
        if (!this.props.location.query.id) return;
        return (
            <button className="btn btn-danger" onClick={this.onDelete}>
                Delete
            </button>
        )
    }

    renderError() {
        if (!this.state.error) return;
        return (
            <div className="alert alert-warning capitalize-first-letter col-margin">
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

    render2() {
        if (this.state.loading > 0)
            return <Loader />
        return (
            <div className="col-12 col-sm-8 col-md-6">
                {this.renderError()}
                <form 
                    method="post" 
                    className="col-margin" 
                    onSubmit={this.onSubmit}
                >
                    <div className="form-group">
                        <label>Name</label>
                        {this.renderFieldError('name')}
                        <input
                            ref={(ref) => (this.name = ref)}
                            type="text"
                            className="form-control dark-form-control"
                            defaultValue={this.state.playServer.name}
                            placeholder="My play server"
                        />
                    </div>
                    <div className="form-group">
                        <label>URL</label>
                        {this.renderFieldError('url')}
                        <input
                            ref={(ref) => (this.url = ref)}
                            type="text"
                            className="form-control dark-form-control"
                            defaultValue={this.state.playServer.url}
                            placeholder="https://example.net"
                        />
                    </div>
                    <div className="form-group">
                        <label>Secret</label>
                        {this.renderFieldError('secret')}
                        <input
                            ref={(ref) => (this.secret = ref)}
                            type="text"
                            className="form-control dark-form-control"
                            defaultValue={this.state.playServer.secret}
                            placeholder="A super long secret"
                        />
                    </div>
                    <button type="submit" className="btn btn-primary m-r-1">
                        Save
                    </button> 
                    {this.renderDeleteButton()}
                </form>

                {this.renderUsersWithAccess()}
            </div>
        )
    }

    render() {
        return (
            <div className="row">
                <div className="col-12">
                    <h1 className="col-margin">Play server</h1>
                </div>
                {this.render2()}
            </div>
        )
    }
}
PlayServer.propTypes = propTypes;

export default withRouter(PlayServer);
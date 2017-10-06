import React from 'react';
import {Link} from 'react-router';
import Loader from 'components/Loader';
import {requireAuthed, getUserId} from 'utils';
import {request} from 'api';

class PlayServers extends React.Component {

    constructor(props) {
        super(props);
        requireAuthed();
        this.state = {
            loading: true,
            playServers: [],
        }
    }

    componentDidMount() {
        this.getPlayServers();
    }

    getPlayServers() {
        this.setState({loading: true});
        request(`/1/users/${getUserId()}/play-servers`, {
            body: {
                per_page: 100,
            }
        }).done(data => {
            this.setState({playServers: data, loading: false});
        });
    }

    renderPlayServers() {
        if (this.state.playServers.length == 0)
            return (
                <div className="alert alert-info">
                    You have no play servers.
                </div>
            );
        return (
            <table className="table">
            <tbody>
            {this.state.playServers.map(s => (
                <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.url}</td>
                    <td width="10px">
                        <Link to={`/play-server?id=${s.id}`}>
                            <i className="fa fa-pencil-square-o"></i>
                        </Link>
                    </td>
                </tr>
            ))}
            </tbody>
            </table>
        )
    }

    render2() {
        if (this.state.loading)
            return <Loader />;
        return (
            <div className="col-12 col-sm-7 col-md-5">
                <Link 
                    to="/play-server"
                    className="btn btn-success col-margin"
                >
                    New play server
                </Link>
                {this.renderPlayServers()}
            </div>
        )
    }

    render() {
        return (
            <div className="row">
                <div className="col-12">
                    <h1 className="col-margin">Play servers</h1>
                </div>
                {this.render2()}
            </div>
        )
    }
}

export default PlayServers;
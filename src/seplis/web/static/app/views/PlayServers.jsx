import React from 'react'
import Loader from 'components/Loader'
import {Link} from "react-router-dom"
import {requireAuthed} from 'utils'
import {request} from 'api'

class PlayServers extends React.Component {

    constructor(props) {
        super(props)
        requireAuthed()
        this.state = {
            loading: true,
            playServers: [],
        }
    }

    componentDidMount() {
        document.title = `Play Servers | SEPLIS`
        this.getPlayServers()
    }

    getPlayServers() {
        this.setState({loading: true})
        request(`/1/play-servers`, {
            body: {
                per_page: 100,
            }
        }).done(data => {
            this.setState({playServers: data, loading: false})
        })
    }

    renderPlayServers() {
        if (this.state.playServers.length == 0)
            return (
                <div className="alert alert-info">
                    You have no play servers.
                </div>
            )
        return (
            <table className="table">
            <tbody>
            {this.state.playServers.map(s => (
                <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.url}</td>
                    <td width="10px">
                        <Link to={`/play-server?id=${s.id}`}>
                            <i className="fas fa-pen-square"></i>
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
            return <Loader />
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

export default PlayServers
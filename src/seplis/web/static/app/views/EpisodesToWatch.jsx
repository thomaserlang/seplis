import React from 'react'
import {request} from 'api'
import Loader from 'components/Loader'
import Pagination from 'components/Pagination'
import EpisodesToWatchList from 'components/shows/EpisodesToWatch.jsx'
import {getEpisodesToWatch} from 'components/shows/EpisodesToWatch.jsx'
import {requireAuthed, locationQuery} from 'utils'

class EpisodesToWatch extends React.Component {

    constructor(props) {
        super(props)
        requireAuthed()
        this.onPageChange = this.pageChange.bind(this)
        this.state = {
            loading: true,
            items: [],
            jqXHR: null,
            page: locationQuery().page || 1,
        }
    }

    componentDidUpdate(prevProps) {
        if (this.props.location !== prevProps.location) {
            this.setState({
                page: locationQuery().page || 1,
                loading: true,
            },() => {
                this.getItems()
            })
        }
    }

    setBrowserPath() {
        this.props.history.push(`${this.props.location.pathname}?page=${this.state.page}`)
    }

    pageChange(e) {
        this.setState({
            page: e.target.value,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.getItems()
        })
    }

    componentDidMount() {
        document.title = `Episodes to Watch | SEPLIS`
        this.getItems()
    }

    getItems() {
        getEpisodesToWatch(60, this.state.page).then((data) => {
            this.setState({
                items: data.items,
                jqXHR: data.jqXHR,
                loading: false,
            })
        })
    }

    render() {
        if (this.state.loading==true)
            return (
                <span>
                    <h2>Episodes to Watch</h2>
                    <Loader />
                </span>
            )
        return (
            <span>
                <div className="row">
                    <div className="col-12 col-sm-9 col-md-10">
                        <h2>Episodes to Watch</h2>
                    </div>
                    <div className="col-sm-3 col-md-2">
                        <Pagination 
                            jqXHR={this.state.jqXHR} 
                            onPageChange={this.onPageChange}
                        />
                    </div>
                </div>
                <EpisodesToWatchList items={this.state.items} />
                <div className="row">
                    <div className="col-sm-9 col-md-10" />
                    <div className="col-sm-3 col-md-2">
                        <Pagination 
                            jqXHR={this.state.jqXHR} 
                            onPageChange={this.onPageChange}
                        />
                    </div>
                </div>
            </span>
        )
    }
}

export default EpisodesToWatch
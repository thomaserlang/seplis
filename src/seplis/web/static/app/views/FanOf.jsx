import React from 'react'
import {request} from 'api'
import {getUserId} from 'utils'
import Loader from 'components/Loader'
import Pagination from 'components/Pagination'
import ShowList from 'components/shows/List.jsx'
import {requireAuthed, locationQuery} from 'utils'

class FanOf extends React.Component {

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
            this.setState(
                {page: locationQuery().page || 1},
                () => {this.getShows()}
            )
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
            this.getShows()
        })
    }

    componentDidMount() {
        this.getShows()
    }

    getShows() {
        let userId = getUserId()
        this.setState({loading: true})
        request(`/1/users/${userId}/fan-of`, {
            query: {
                page: this.state.page,
                per_page: 60,
            }
        }).done((shows, textStatus, jqXHR) => {
            this.setState({
                shows: shows,
                loading: false,
                jqXHR: jqXHR,
                totalCount: jqXHR.getResponseHeader('X-Total-Count'),
            })
        })
    }

    render() {
        if (this.state.loading==true)
            return (
                <span>
                    <h2>Fan of {this.state.totalCount} shows</h2>
                    <Loader />
                </span>
            )
        return (
            <span>
                <div className="row">
                    <div className="col-12 col-sm-9 col-md-10">
                        <h2>
                            Fan of {this.state.totalCount} shows
                        </h2>
                    </div>
                    <div className="col-sm-3 col-md-2">
                        <Pagination 
                            jqXHR={this.state.jqXHR} 
                            onPageChange={this.onPageChange}
                        />
                    </div>
                </div>
                <ShowList shows={this.state.shows} />
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

export default FanOf
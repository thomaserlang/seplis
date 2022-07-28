import React from 'react'
import {request} from 'api'
import {getUserId} from 'utils'
import Loader from 'components/Loader'
import Pagination from 'components/Pagination'
import ShowList from 'components/shows/List.jsx'
import ListMode from 'components/ListMode.jsx'
import SelectGenres from 'components/SelectGenres.jsx'
import {requireAuthed, locationQuery} from 'utils'

class Following extends React.Component {

    constructor(props) {
        super(props)
        requireAuthed()
        this.state = {
            loading: true,
            items: [],
            jqXHR: null,
            page: locationQuery().page || 1,
            sort: locationQuery().sort || 'followed_at',
            genre: locationQuery().genre || '',
        }
    }    

    componentDidUpdate(prevProps) {
        if (this.props.location !== prevProps.location) {
            this.setState({
                page: locationQuery().page || 1,
                sort: locationQuery().sort || 'followed_at',
            },
                () => {this.getShows()}
            )
        }
    }

    setBrowserPath() {
        this.props.history.push(
            `${this.props.location.pathname}?page=${this.state.page}&sort=${this.state.sort}&genre=${this.state.genre}`
        )
    }

    pageChange = (e) => {
        this.setState({
            page: e.target.value,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.getShows()
        })
    }

    listModeChange = () => {
        this.forceUpdate()
    }

    sortChange = (e) => {
        this.setState({
            sort: e.target.value,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.getShows()
        })
    }

    genreChange = (genre) => {
        this.setState({
            genre: genre,
            page: 1,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.getShows()
        })
    }

    componentDidMount() {
        document.title = `Following | SEPLIS`
        this.getShows()
    }

    getShows() {
        let userId = getUserId()
        this.setState({loading: true})
        request(`/1/users/${userId}/fan-of`, {
            query: {
                page: this.state.page,
                per_page: 60,
                expand: 'user_rating',
                sort: this.state.sort,
                genre: this.state.genre,
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
            return <>
                <h2>Following {this.state.totalCount} shows</h2>
                <Loader />
            </>
        return <>
            <div className="d-md-flex mb-2">
                <div>
                    <h2 className="mb-2">
                        Following {this.state.totalCount} shows
                    </h2>
                </div>
                <div className="ml-auto d-md-flex">
                    <div className="mr-2 mb-2">
                        <ListMode onModeChange={this.listModeChange} />
                    </div>
                    <div className="d-flex">
                        <div className="mr-2 mb-2">
                            <SelectGenres onChange={this.genreChange} selected={this.state.genre} />
                        </div>
                        <div className="mr-2 mb-2">
                            <select 
                                className="form-control" 
                                onChange={this.sortChange} 
                                value={this.state.sort}
                            >
                                <option value="followed_at">Sort: Followed at</option>
                                <option value="user_rating">Sort: Rating</option>
                            </select>
                        </div>
                        <div className="d-sm-block d-none">
                            <Pagination 
                                jqXHR={this.state.jqXHR} 
                                onPageChange={this.pageChange}
                            />
                        </div>
                    </div>
                </div>
            </div>
            <ShowList listMode="" shows={this.state.shows} />
            <div className="d-flex">
                <div className="ml-auto">
                    <Pagination 
                        jqXHR={this.state.jqXHR} 
                        onPageChange={this.pageChange}
                    />
                </div>
            </div>
        </>
    }
}

export default Following
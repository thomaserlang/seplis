import React from 'react'
import {request} from 'api'
import {getUserId} from 'utils'
import Loader from 'components/Loader'
import Pagination from 'components/Pagination'
import List from 'components/movies/List.jsx'
import ListMode from 'components/ListMode.jsx'
import {requireAuthed, locationQuery} from 'utils'

class MoviesStared extends React.Component {

    constructor(props) {
        super(props)
        requireAuthed()
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
            },
                () => {this.getmovies()}
            )
        }
    }

    setBrowserPath() {
        this.props.history.push(
            `${this.props.location.pathname}?page=${this.state.page}`
        )
    }

    pageChange = (e) => {
        this.setState({
            page: e.target.value,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.getmovies()
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
            this.getmovies()
        })
    }

    genreChange = (genre) => {
        this.setState({
            genre: genre,
            page: 1,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.getmovies()
        })
    }

    componentDidMount() {
        document.title = `Stared Movies | SEPLIS`
        this.getmovies()
    }

    getmovies() {
        this.setState({loading: true})
        request(`/1/users/me/movies-stared`, {
            query: {
                page: this.state.page,
                per_page: 60,
            }
        }).done((movies, textStatus, jqXHR) => {
            this.setState({
                movies: movies,
                loading: false,
                jqXHR: jqXHR,
                totalCount: jqXHR.getResponseHeader('X-Total-Count'),
            })
        })
    }

    render() {
        if (this.state.loading==true)
            return <>
                <h2>Stared {this.state.totalCount} movies</h2>
                <Loader />
            </>
        return <>
            <div className="d-md-flex mb-2">
                <div>
                    <h2 className="mb-2">
                        Stared {this.state.totalCount} movies
                    </h2>
                </div>
                <div className="ml-auto d-md-flex">
                    <div className="mr-2 mb-2">
                        <ListMode onModeChange={this.listModeChange} />
                    </div>
                    <div className="d-flex">
                        <div className="d-sm-block d-none">
                            <Pagination 
                                jqXHR={this.state.jqXHR} 
                                onPageChange={this.pageChange}
                            />
                        </div>
                    </div>
                </div>
            </div>
            <List listMode="" movies={this.state.movies} />
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

export default MoviesStared
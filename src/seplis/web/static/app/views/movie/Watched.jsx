import React from 'react'
import Loader from 'components/Loader'
import Pagination from 'components/Pagination'
import MovieList from 'components/movies/List.jsx'
import ListMode from 'components/ListMode.jsx'
import {request} from 'api'
import {requireAuthed, locationQuery} from 'utils'

class MoviesWatched extends React.Component {

    constructor(props) {
        super(props)
        requireAuthed()
        this.state = {
            loading: true,
            movies: [],
            jqXHR: null,
            page: locationQuery().page || 1,
            totalCount: '...',
        }
    }    

    componentDidUpdate(prevProps) {
        if (this.props.location !== prevProps.location) {
            this.setState({
                page: locationQuery().page || 1,
                loading: true,
            },() => {
                this.getMovies()
            })
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
            this.getMovies()
        })
    }

    listModeChange = () => {
        this.forceUpdate()
    }

    componentDidMount() {
        document.title = `Movies Watched | SEPLIS`
        this.getMovies()
    }

    getMovies() {
        this.setState({loading: true})
        request(`/1/users/me/movies-watched`, {
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
            return (
                <span>
                    <h2>Watched {this.state.totalCount} movies</h2>
                    <Loader />
                </span>
            )
        return <>
            <div className="d-md-flex mb-2">
                <div>                        
                    <h2 className="mb-2">Watched {this.state.totalCount} movies</h2>
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
            <MovieList listMode="" movies={this.state.movies} />
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

export default MoviesWatched
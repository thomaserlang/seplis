import React, { useEffect, useState } from 'react'
import {Route, Link} from 'react-router-dom'
import {request} from 'api'
import Loader from 'seplis/components/Loader'
import MovieNav from 'seplis/components/movies/Nav'
import StarButton from 'seplis/components/movies/StarButton'

import MovieMain from './Main'
import MovieEdit from './Edit'

export default function Movie(props) {
    const [movie, setMovie] = useState(null)
    
    useEffect(() => {        
        request(`/1/movies/${props.match.params.movieId}`).done((data) => {
            setMovie(data)
        })
    }, [])

    if (!movie)
        return <Loader hcenter={true} />

    if ((!movie.title) && !(props.location.pathname.endsWith('/edit')))
        return ImportingMessage(movie)

    return <div>
        <div className="row">
            <div className="col-4 col-sm-4 col-md-4 col-margin d-none d-sm-block">
                <img 
                    src={movie.poster_image!=null?movie.poster_image.url + '@SX360':''} 
                    width="100%" 
                />
            </div>
            <div className="col-4 d-sm-none" />

            <div className="col-12 col-sm-8">
                <div className="show-header mb-2">
                    <h1 className="title">
                        {movie.title}
                        &nbsp;
                        <small className="text-muted">{movie.release_date!=null?movie.release_date.substring(0,4):''}</small>
                    </h1>
                    <div className="ml-auto">
                        <StarButton movieId={movie.id} />
                    </div>
                </div>

                <MovieNav movieId={parseInt(movie.id)} />
                <Route exact path="/movie/:movieId" render={(props) => <MovieMain {...props} movie={movie} />} />
                <Route path="/movie/:movieId/edit" render={(props) => <MovieEdit {...props} movie={movie} />} />
            </div>
        </div>
    </div>
}

function ImportingMessage(movie) {
    return (
        <center>
            <h1>The movie is currently in the import queue</h1>
            <h2>Check back later!</h2>
            <Link 
                className="btn btn-warning" 
                to={`/movie/${movie.id}/edit`}
            >
                Edit movie
            </Link>
            <Loader />
        </center>
    )
}
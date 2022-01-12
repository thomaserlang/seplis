import React from 'react'
import {Route, Link} from 'react-router-dom'
import {request} from 'api'
import {isAuthed, getUserId} from 'seplis/utils'

import Loader from 'seplis/components/Loader'
import FanButton from 'seplis/components/shows/FanButton'
import ShowNav from 'seplis/components/shows/ShowNav'

import ShowMain from './Main'
import ShowSeasons from './Seasons'
import ShowStats from './Stats'
import ShowInfo from './Info'
import ShowEdit from './Edit'
import Images from './Images'
import NewImage from './NewImage'

import './Show.scss'

class Show extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            show: document.seplis_tv_show,
        };
    }

    renderShow() {
        let show = this.state.show;
        return (
            <div>
                <div className="row">
                    <div className="col-4 col-sm-4 col-md-4 col-margin d-none d-sm-block">
                        <img 
                            src={show.poster_image!=null?show.poster_image.url + '@SX360':''} 
                            width="100%" 
                        />
                    </div>
                    <div className="col-4 d-sm-none" />

                    <div className="col-12 col-sm-8">
                        <div className="show-header mb-2">
                            <h1 className="title">
                                {show.title}
                                &nbsp;
                                <small className="text-muted">{show.premiered!=null?show.premiered.substring(0,4):''}</small>
                            </h1>
                            <div className="ml-auto">
                                <FanButton showId={show.id} />
                            </div>
                        </div>

                        <ShowNav showId={parseInt(this.state.show.id)} />
                        <Route exact path="/show/:showId" render={(props) => <ShowMain {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/main" render={(props) => <ShowMain {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/info" render={(props) => <ShowInfo {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/seasons" render={(props) => <ShowSeasons {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/images" render={(props) => <Images {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/new-image" render={(props) => <NewImage {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/stats" render={(props) => <ShowStats {...props} show={this.state.show} />} />
                        <Route path="/show/:showId/edit" render={(props) => <ShowEdit {...props} show={this.state.show} />} />
                    </div>
                </div>
            </div>
        )
    }

    renderShowImporting() {
        setTimeout(() => {
            location.reload();
        }, 5000);
        return (
            <center>
                <h1>The show is currently in the import queue</h1>
                <h2>Check back later!</h2>
                <Link 
                    className="btn btn-warning" 
                    to={`/show/${this.state.show.id}/edit`}
                >
                    Edit show
                </Link>
                <Loader />
            </center>
        )
    }

    render() {
        if (!this.state.show) {
            return (
                <Loader />
            )
        } 
        else if (
            (this.state.show.status == 0)
            && !(this.props.location.pathname.endsWith('/edit'))
            && (this.state.show.importers.info != null)) {
            return this.renderShowImporting();
        }
        else {
            return this.renderShow();
        }
    }
}

export default Show;
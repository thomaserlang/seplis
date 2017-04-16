import React from 'react';
import {request} from 'api';
import {isAuthed} from 'utils';

import Loader from 'components/Loader';
import FanButton from 'components/shows/FanButton';
import ShowNav from 'components/shows/ShowNav';

const propTypes = {
    params: React.PropTypes.object.isRequired,
}

class Show extends React.Component {

    constructor(props) {
        super(props);
        this.state = {show: null};
        this.getShow();
    }

    getShow() {
        let query = {};
        if (isAuthed()) {
            query.append = 'is_fan';
        }
        request(`/1/shows/${parseInt(this.props.params.showId)}`, {
            query: query,
        }).success(show => {
            this.setState({show: show});
        });
    }

    renderShow() {
        let show = this.state.show;
        return (
            <div>
                <div className="row">
                    <div className="col-12">
                        <div className="btn-fan__pull-left">
                            <FanButton showId={show.id} isFan={show.is_fan || false} />
                        </div>
                        <h1>
                            {show.title}
                            &nbsp;
                            <small className="text-muted">{show.premiered!=null?show.premiered.substring(0,4):''}</small>
                        </h1>
                    </div> 

                    <div className="col-4 hidden-sm-up" />
                    <div className="col-4 col-sm-4 col-md-4 col-margin">
                        <img 
                            src={show.poster_image!=null?show.poster_image.url + '@SX360':''} 
                            width="100%" 
                        />
                    </div>
                    <div className="col-4 hidden-sm-up" />

                    <div className="col-12 col-sm-8">
                        <ShowNav showId={parseInt(this.state.show.id)} />
                        {React.cloneElement(this.props.children, {show: show})}
                    </div>
                </div>
            </div>
        )
    }

    renderShowImporting() {
        setTimeout(() => {
            this.getShow();
        }, 5000);
        return (
            <center>
                <h1>The show is currently in the import queue</h1>
                <h2>Check back later!</h2>
                <a 
                    className="btn btn-warning" 
                    href={`/show/${this.state.show.id}/edit`}
                >
                    Edit show
                </a>
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
Show.propTypes = propTypes;

export default Show;
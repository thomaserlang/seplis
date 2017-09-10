import React from 'react';
import {browserHistory} from 'react-router';
import {request} from 'api';
import {getUserId} from 'utils';
import Loader from 'components/Loader';
import Pagination from 'components/Pagination';
import ShowList from 'components/shows/List.jsx';

class FanOf extends React.Component {

    constructor(props) {
        super(props);
        this.onPageChange = this.pageChange.bind(this);
        this.state = {
            loading: true,
            shows: [],
            jqXHR: null,
            totalCount: '...',
            page: this.props.location.query.page || 1,
        }
    }

    setBrowserPath() {
        browserHistory.push({
            pathname: '/fan-of',
            query: { 
                page: this.state.page,
            },
        });
    }

    pageChange(e) {
        this.setState({
            page: e.target.value,
            loading: true,
        }, () => {
            this.setBrowserPath();
            this.getShows();
        });
    }

    componentDidMount() {
        this.getShows();
    }

    getShows() {
        let userId = getUserId();
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
            });
        });
    }

    render() {
        if (this.state.loading==true)
            return (
                <span>
                    <h1>Fan of {this.state.totalCount} shows</h1>
                    <Loader />
                </span>
            );
        return (
            <span>
                <div className="row">
                    <div className="col-12 col-sm-9 col-md-10">
                        <h1>
                            Fan of {this.state.totalCount} shows
                        </h1>
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

export default FanOf;
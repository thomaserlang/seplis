import React from 'react';
import {browserHistory} from 'react-router';
import {request} from 'api';
import Loader from 'components/Loader';
import Pagination from 'components/Pagination';
import ShowsRecentlyAired from 'components/shows/Countdown.jsx';
import {getItems} from 'components/shows/Countdown.jsx';
import {requireAuthed} from 'utils';

class Countdown extends React.Component {

    constructor(props) {
        super(props);
        requireAuthed();
        this.onPageChange = this.pageChange.bind(this);
        this.state = {
            loading: true,
            items: [],
            jqXHR: null,
            page: this.props.location.query.page || 1,
        }
    }

    setBrowserPath() {
        browserHistory.push({
            pathname: this.props.location.pathname,
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
            this.getItems();
        });
    }

    componentDidMount() {
        this.getItems();
    }

    getItems() {
        getItems(60, this.state.page).then((data) => {
            this.setState({
                items: data.items,
                jqXHR: data.jqXHR,
                loading: false,
            })
        });
    }

    render() {
        if (this.state.loading==true)
            return (
                <span>
                    <h2>Countdown</h2>
                    <Loader />
                </span>
            );
        return (
            <span>
                <div className="row">
                    <div className="col-12 col-sm-9 col-md-10">
                        <h2>Countdown</h2>
                    </div>
                    <div className="col-sm-3 col-md-2">
                        <Pagination 
                            jqXHR={this.state.jqXHR} 
                            onPageChange={this.onPageChange}
                        />
                    </div>
                </div>
                <ShowsRecentlyAired items={this.state.items} />
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

export default Countdown;
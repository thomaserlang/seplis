import React from 'react';
import {request} from 'api';
import {getUserId} from 'utils';
import Loader from 'components/Loader';
import ShowList from 'components/shows/List';

const oneDay = 24*60*60*1000;
const weekdays = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
];

class Main extends React.Component {

    constructor(props) {
        super();
        this.state = {
            loading: true,
            data: [],
        }
    }

    componentDidMount() {
        this.getData();
    }

    getData() {
        request(`/1/users/${getUserId()}/air-dates`)
            .done((data) => {
                this.setState({
                    loading: false,
                    data: data,
                });
            });
    }

    renderWeekday(date) {
        let d = new Date(date);
        return weekdays[d.getDay()];
    }

    renderHeaderDate(date) {
        let d1 = Date.parse(date);
        let d2 = Date.now();
        let days = Math.round(
            Math.ceil(
                (d1 - d2) / oneDay
            )
        );
        switch (days) {
            case -1:
                return (<span>Yesterday <small className="text-muted">{this.renderWeekday(date)}</small></span>);
                break;
            case 0:
                return (<span>Today <small className="text-muted">{this.renderWeekday(date)}</small></span>);;
                break;
            case 1: 
                return (<span>Tomorrow <small className="text-muted">{this.renderWeekday(date)}</small></span>);;
                break;
            default:
                return this.renderWeekday(date);
                break;
        }
    }

    renderMain() {
        if (this.state.data.length == 0)
            return (
                <div className="alert alert-info">
                    <h1>There's nothing to watch this week!</h1>
                    But, how can this be?<br />
                    Well, you're properly not following of any shows that has 
                    episodes airing this week.
                </div>
            );
        else
            return (
                <span>
                    {this.state.data.map(a => (
                    <span key={a.air_date}>
                        <h3 className="header header-border" title={a.air_date}>
                            {this.renderHeaderDate(a.air_date)}
                        </h3>
                        <ShowList 
                            shows={a.shows} 
                        />
                    </span>
                    ))}
                </span>
            );
    }

    render() {
        if (this.state.loading)
            return <Loader />;
        return this.renderMain();
    }
}

export default Main;
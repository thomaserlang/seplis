import React from 'react';
import Loader from 'seplis/components/Loader';
import ShowsWatched, {getWatched} from 'components/shows/Watched';
import ShowsCountdown, {getCountdown} from 'components/shows/Countdown';
import ShowsRecentlyAired, {getRecentlyAired} from 'components/shows/RecentlyAired';
import ShowsEpisodesToWatch, {getEpisodesToWatch} from 'components/shows/EpisodesToWatch';
import {requireAuthed} from 'utils';

class Main extends React.Component {
    
    constructor(props) {
        super(props);
        requireAuthed();
        this.visChange = this.visibilitychange.bind(this);
        document.addEventListener('visibilitychange', this.visChange);
        this.state = {
            key: 0,
            loading: true,
            failed: false,
        }
    }

    componentDidMount() {
        this.getData();
    }

    componentWillUnmount() {
        document.removeEventListener('visibilitychange', this.visChange);
    }

    getData() {
        this.setState({
            loading: true,
            failed: false,
        });
        Promise.all([
            getWatched(6, 1),
            getCountdown(6, 1),
            getRecentlyAired(6, 1),
            getEpisodesToWatch(6, 1),
        ]).then((result) => {
            this.setState({
                'loading': false,
                'failed': false,
                'watched': result[0].items,
                'countdown': result[1].items,
                'recentlyWatched': result[2].items,
                'episodesToWatch': result[3].items,
            })
        }).catch(() => {
            this.setState({
                loading: false,
                failed: true,
                key: this.state.key + 1,
            })
        });
    }

    visibilitychange() {
        if (document.hidden) return;
        this.getData();
    }

    render() {
        if (this.state.failed)
            return (
                <div className="alert alert-warning">
                    Failed to load, try refreshing.
                </div>
            )
        if (this.state.loading)
            return <Loader />;
        return (
            <span>
            <h2 className="header header-border">
                <a href="/shows-watched">Recently watched</a>
            </h2>    
            <div className="slider mb-2">
                <ShowsWatched key={`sw-${this.state.key}`} items={this.state.watched} />
            </div>

            <h2 className="header header-border">
                <a href="/recently-aired">Recently Aired</a>
            </h2>
            <div className="slider mb-2">
                <ShowsRecentlyAired key={`sra-${this.state.key}`} items={this.state.recentlyWatched} />
            </div>

            <h2 className="header header-border">
                <a href="/countdown">Countdown</a>
            </h2>
            <div className="slider mb-2">
                <ShowsCountdown key={`sc-${this.state.key}`} items={this.state.countdown} />
            </div>            

            <h2 className="header header-border">
                <a href="/episodes-to-watch">Episodes To Watch</a>
            </h2>
            <div className="slider mb-2">
                <ShowsEpisodesToWatch key={`etw-${this.state.key}`} items={this.state.episodesToWatch} />
            </div>
            </span>
        )
    }
}

export default Main;
import React from 'react';
import ShowsWatched from 'components/shows/Watched';
import ShowsCountdown from 'components/shows/Countdown';
import ShowsRecentlyAired from 'components/shows/RecentlyAired';
import ShowsEpisodesToWatch from 'components/shows/EpisodesToWatch';
import {requireAuthed} from 'utils';

class Main extends React.Component {
    
    constructor(props) {
        super(props);
        requireAuthed();
        this.visChange = this.visibilitychange.bind(this);
        document.addEventListener('visibilitychange', this.visChange);
        this.state = {
            key: 0,
        }
    }

    componentWillUnmount() {
        document.removeEventListener('visibilitychange', this.visChange);
    }

    visibilitychange() {
        if (document.hidden) return;
        this.setState({
            key: this.state.key + 1,
        })
    }

    render() {
        return (
            <span>
            <h2 className="header"><a href="/shows-watched">Recently watched</a></h2>    
            <div className="slider col-margin">
                <ShowsWatched key={`sw-${this.state.key}`} perPage={6} />
            </div>

            <h2 className="header"><a href="/countdown">Countdown</a></h2>
            <div className="slider col-margin">
                <ShowsCountdown key={`sc-${this.state.key}`} perPage={6} />
            </div>
            
            <h2 className="header"><a href="/recently-aired">Recently Aired</a></h2>
            <div className="slider col-margin">
                <ShowsRecentlyAired key={`sra-${this.state.key}`} perPage={6} />
            </div>

            <h2 className="header"><a href="/episodes-to-watch">Episodes To Watch</a></h2>
            <div className="slider col-margin">
                <ShowsEpisodesToWatch  key={`etw-${this.state.key}`} perPage={6} />
            </div>
            </span>
        )
    }
}

export default Main;
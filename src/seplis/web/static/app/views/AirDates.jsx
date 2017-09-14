import React from 'react';
import ShowsAirDates from 'components/shows/AirDates';
import {requireAuthed} from 'utils';

class AirDates extends React.Component {    

    constructor(props) {
        super(props);
        requireAuthed();
    }


    render() {
        return (
            <ShowsAirDates />
        )
    }
}

export default AirDates;
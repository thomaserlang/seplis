import React from 'react';
import PropTypes from 'prop-types';
import EditAlternativeTitles from '../shows/EditAlternativeTitles';

const propTypes = {
    movie: PropTypes.object,
}

const externals = [
    {
        'key': 'imdb',
        'title': 'IMDb',
        'required': true,
    },
]

class EditFields extends React.Component {

    constructor(props) {
        super(props);
        this.onInputChange = this.inputChanged.bind(this);
        let movie = props.movie || {};
        let movieExternals = movie.externals || {};
        // Fill state
        this.state = {
            alternative_titles: movie.alternative_titles?movie.alternative_titles.slice():[],
        }
        for (let external of externals) {
            this.state[`externals.${external.key}`] = movieExternals[external.key] || '';
        }
    }

    inputChanged(e) {
        let s = {};
        let name = e.target.name;
        let value = e.target.value;
        s[name] = value;
        this.setState(s);
    }

    renderExternals() {
        return (
            externals.map((external) => (
                <fieldset key={external.key} className="form-group">
                    <label>{external.title} ID {external.required?<b>*</b>:''}</label>                    
                    <input 
                        name={`externals.${external.key}`} 
                        className="form-control" 
                        required={external.required}
                        value={this.state[`externals.${external.key}`]}
                        onChange={this.onInputChange}
                    />
                </fieldset>
            ))
        )
    }

    render() {
        return (
            <div className="row">
                <div className="col-md-6">
                    <h3>Externals</h3>
                    {this.renderExternals()}
                </div>

                <div className="col-md-6">
                    <h3>General</h3>
                    <fieldset className="form-group">
                        <label>Alternative titles</label>
                        <EditAlternativeTitles 
                            options={this.state.alternative_titles} 
                        />
                    </fieldset>
                </div>
            </div>
        )
    }
}
EditFields.propTypes = propTypes;

export default EditFields;
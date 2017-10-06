import React from 'react';
import PropTypes from 'prop-types';
import EditAlternativeTitles from './EditAlternativeTitles';
import {request} from 'api';

const propTypes = {
    show: PropTypes.object,
}

const externals = [
    {
        'key': 'imdb',
        'title': 'IMDb',
        'required': true,
        'importer_info': false,
        'importer_episodes': false,
    },
    {
        'key': 'tvmaze',
        'title': 'TVMaze',
        'required': false,
        'importer_info': true,
        'importer_episodes': true,
    },
    {
        'key': 'thetvdb',
        'title': 'TheTVDB',
        'required': false,
        'importer_info': true,
        'importer_episodes': true,
    },
]

const importerTypes = [
    'info',
    'episodes',
]

class EditFields extends React.Component {

    constructor(props) {
        super(props);
        this.onImporterSelected = this.importerSelected.bind(this);
        this.onInputChange = this.inputChanged.bind(this);
        let show = props.show || {};
        let showexternals = show.externals || {};
        let importers = show.importers || {};
        // Fill state
        this.state = {
            'importers.info': importers.info || '',
            'importers.episodes': importers.episodes || '',
            alternative_titles: show.alternative_titles?show.alternative_titles.slice():[],
            episode_type: show.episode_type || 2,
        }
        for (let external of externals) {
            this.state[`externals.${external.key}`] = showexternals[external.key] || '';
        }
    }

    importerSelected(e) {
        let s = {}
        s[e.target.name] = e.target.value;
        for (let type of importerTypes) {
            if (`importers.${type}` == e.target.name)
                continue;
            if (this.state[`importers.${type}`] === '') {
                s[`importers.${type}`] = e.target.value;
            }
        }
        this.setState(s);
    }

    inputChanged(e) {
        let s = {};
        let name = e.target.name;
        let value = e.target.value;
        s[name] = value;
        this.setState(s);
        if ((name.startsWith('externals.')) && (value != '')) {
            let query = {};
            query[name.substring(name.indexOf('.')+1, name.length)] = value;
            this.lookupExternals(query);
        }
    }

    lookupExternals(query) {
        request('/api/tvmaze-show-lookup', {
            localRequest:true,
            query: query,
        }).done(data => {
            let s = {'externals.tvmaze': data.id}
            for (let key in data.externals) {
                if (`externals.${key}` in this.state) {
                    s[`externals.${key}`] = data.externals[key];
                }
            }
            this.setState(s);
        })
    }

    renderImporter(type) {
        let importers = [];
        for (let external of externals) {
            if (external['importer_'+type]) {
                importers.push(external);
            }
        }
        return (
            <fieldset className="form-group" key={type}>
                <label>Import {type} from</label>
                <select 
                    name={'importers.'+type} 
                    className="form-control importers" 
                    onChange={this.onImporterSelected}
                    value={this.state[`importers.${type}`]}
                >
                    <option value=""></option>
                    {importers.map((external) => (
                        <option key={external.key} value={external.key}>
                            {external.title}
                        </option>
                    ))}
                </select>
            </fieldset>
        )
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
                    {external.required?
                        <small className="text-muted"> Required to prevent show duplication.</small>:
                        ''
                    }
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

                    <h3>Importers</h3>
                    {importerTypes.map((type) => (
                        this.renderImporter(type)
                    ))}
                </div>

                <div className="col-md-6">
                    <h3>General</h3>
                    <fieldset className="form-group">
                        <label>Alternative titles</label>
                        <EditAlternativeTitles 
                            options={this.state.alternative_titles} 
                        />
                    </fieldset>

                    <fieldset className="form-group">
                        <label>Episode type</label>
                        <select 
                            name="episode_type"
                            className="form-control"
                            defaultValue={this.state.episode_type}
                        >
                            <option value="1">Absolute number</option>
                            <option value="2">Season episode</option>
                            <option value="3">Air date</option>
                        </select>
                    </fieldset>
                </div>
            </div>
        )
    }
}
EditFields.propTypes = propTypes;

export default EditFields;
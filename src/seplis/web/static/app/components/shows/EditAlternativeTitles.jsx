import React from 'react';

import $ from 'jquery';
import 'select2';
import 'select2/dist/css/select2.css';

const propTypes = {
    options: React.PropTypes.arrayOf(React.PropTypes.string),
}

const defaultProps = {
    options: [],
}

class EditAlternativeTitles extends React.Component {

    componentDidMount() {
        $('select#alternative-titles').select2({
            tags: true,
        });
    }

    render() {
        return (
            <span style={{color:'#000000'}}>
                <select 
                    name="alternative_titles"
                    id="alternative-titles"
                    className="form-control"
                    defaultValue={this.props.options}
                    multiple
                >
                    {this.props.options.map((title) => (
                        <option key={title} value={title}>{title}</option>
                    ))}
                </select>
            </span>
        );
    }
}
EditAlternativeTitles.propTypes = propTypes;
EditAlternativeTitles.defaultProps = defaultProps;

export default EditAlternativeTitles;
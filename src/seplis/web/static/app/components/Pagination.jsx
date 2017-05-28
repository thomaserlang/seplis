import React from 'react';
import PropTypes from 'prop-types';
import LinkParser from 'parse-link-header';

const propTypes = {
    jqXHR: PropTypes.object.isRequired,
    onPageChange: PropTypes.func,
}

class Pagination extends React.Component {

    constructor(props) {
        super(props);
        this.state = this.parseJqXHR();
        this.onPageChange = this.pageChange.bind(this);
    }

    componentWillReceiveProps(nextProps) {
        this.setState(
            this.parseJqXHR(nextProps.jqXHR)
        );
    }

    pageChange(e) {
        this.state.page = e.target.value;
        if (this.props.onPageChange != undefined) 
            this.props.onPageChange(e);
    }

    parseJqXHR(jqXHR) {
        return {
            pages: this.props.jqXHR.getResponseHeader('X-Total-Pages'),
            page: this.props.jqXHR.getResponseHeader('X-Page'),
        };
    }

    renderOptions() {
        let options = [];
        for (let i = 1; i <= this.state.pages; i++) {
            options.push(
                <option 
                    key={i} 
                    value={i}
                >
                    Page {i}
                </option>
            );
        }
        return options;
    }

    render() {
        if (this.state.pages <= 1)
            return null;
        return (
            <select
                className="form-control col-margin"
                onChange={this.onPageChange}
                value={this.state.page}
            >
                {this.renderOptions()}
            </select>
        )
    }
}
Pagination.propTypes = propTypes;

export default Pagination;
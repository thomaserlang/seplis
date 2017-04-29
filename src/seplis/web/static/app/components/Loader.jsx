import React from 'react';
import PropTypes from 'prop-types';
import ClassNames from 'classnames';

import './Loader.scss';

const propTypes = {
    hcenter: PropTypes.boolean,
}

const defaultProps = {
    hcenter: false,
}

class Loader extends React.Component {

    render() {        
        let cls = ClassNames({
            loader: true,
            'loader-hcenter': this.props.hcenter,
        });
        return (
            <div className={cls}></div>
        )
    }

}
Loader.propTypes = propTypes;
Loader.defaultProps = defaultProps;

export default Loader;
import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'

const propTypes = {
    onModeChange: PropTypes.func,
}

class ListMode extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            listMode: localStorage.getItem('listMode') || 'grid',
        }
    }

    modeChange = (e) => {
        e.target.blur()
        let t = e.currentTarget.dataset.type
        localStorage.setItem('listMode', t)
        this.setState({
            listMode: t,
        })
        if (this.props.onModeChange != undefined) 
            this.props.onModeChange(t)
    }

    renderButton(t) {
        let btn = ClassNames({
            btn: true,
            'btn-info': this.state.listMode == t,
            'btn-dark': this.state.listMode != t,
        })
        let i = ClassNames({
            fas: true,
            'fa-th-large': t == 'grid',
            'fa-bars': t == 'list',
        })
        return <button 
            onClick={this.modeChange} 
            className={btn}
            data-type={t}>
                <i className={i}></i>
        </button>
    }

    render() {
        return <>
            {this.renderButton('grid')}
            {this.renderButton('list')}
        </>
    }
}
ListMode.propTypes = propTypes

export default ListMode

                        
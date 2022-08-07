import React from 'react'
import PropTypes from 'prop-types'
import ClassNames from 'classnames'

import './VolumeBar.scss'

const propTypes = {
    onChange: PropTypes.func,
}

class VolumeBar extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            percent: (localStorage.getItem('volume') || 1)*100,
            show: false,
            muted: false,
        }
    }

    componentDidMount() {
        let volume = localStorage.getItem('volume') || 1
        if (this.props.onChange)
            this.props.onChange(volume)
        document.addEventListener('click', this.onDocumentClick)
        document.addEventListener('ontouchstart', this.onDocumentClick)
    }

    componentWillUnmount() {
        document.removeEventListener('click', this.onDocumentClick)
        document.removeEventListener('ontouchstart', this.onDocumentClick)
    }
    
    onDocumentClick = (e) => {
        if (!this.icon.contains(e.target)) {
            this.setState({show: false})
        }
    }

    onSliderMouseMove = (event) => {
        if (event.buttons != 1) return
        this.onSliderClick(event)
    }

    onSliderClick = (event) => {
        event.preventDefault()
        event.stopPropagation()
        const scrubber = event.target.querySelector('.scrubber')
        const rect = scrubber.getBoundingClientRect()
        let y = event.clientY - rect.top;
        if (y > scrubber.offsetHeight)
            y = scrubber.offsetHeight
        if (y < 0)
            y = 0
        y = scrubber.offsetHeight - y
        let norm = 1 / scrubber.offsetHeight
        let volume = norm*y
        if (volume < 0)
            volume = 0
        this.setState({percent: volume*100})
        if (this.props.onChange)
            this.props.onChange(volume)
        localStorage.setItem('volume', volume)
    }

    onIconClick = (event) => {
        this.setState({show: !this.state.show})
    }

    renderBar() {
        if (!this.state.show) return
        return (
            <div 
                className="text-box volume-slider"
                onMouseMove={this.onSliderMouseMove}
                onClick={this.onSliderClick}
            >
                <div className="scrubber">
                    <div 
                        className="scrubber-percentage" 
                        style={{height: this.state.percent+'%'}}
                    />
                    <div 
                        className="scrubber-head"
                        style={{bottom: this.state.percent+'%'}}
                    />
                </div>
            </div>
        )
    }

    render() {
        let volume = ClassNames({
            fa: true,
            'fa-volume-up': (this.state.percent >= 50) && !this.state.muted,
            'fa-volume-down': (this.state.percent < 50) && 
                (this.state.percent >= 1) && !this.state.muted,
            'fa-volume-off': (this.state.percent < 1) || this.state.muted,
        })
        return <>
            <i 
                className={volume} 
                onClick={this.onIconClick}
                ref={(ref) => this.icon = ref}
            />
            {this.renderBar()}
        </>
    }
}
VolumeBar.propTypes = propTypes

export default VolumeBar
import React from 'react'
import PropTypes from 'prop-types'
import {secondsToTime} from 'utils'

import './Slider.scss'

const propTypes = {
    duration: PropTypes.number.isRequired,
    onReturnCurrentTime: PropTypes.func.isRequired,
    onNewTime: PropTypes.func.isRequired,
}

class Slider extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            currentTime: 0,
            hoverTime: null,
            drag: false,
        }
        this.timerGetCurrentTime = null
    }

    componentDidMount() {
        this.getCurrentTime()
    }

    componentWillUnmount() {
        clearTimeout(this.timerGetCurrentTime)
        this.timerGetCurrentTime = null
    }

    sliderClick = (event) => {
        let x = this.getEventXOffset(event)
        let norm = this.props.duration / this.slider.offsetWidth
        var newTime = Math.trunc(norm*x)
        this.setState({
            currentTime: newTime,
            hoverTime: null,
            drag: false,
        })
        this.props.onNewTime(newTime)
    }

    mouseMove = (event) => {
        let x = this.getEventXOffset(event)
        let norm = this.props.duration / this.slider.offsetWidth
        let newTime = Math.trunc(norm*x)
        if (newTime > this.props.duration)
            newTime = this.props.duration
        this.setState({
            hoverTime: newTime,
            drag: event.buttons == 1,
        })
    }

    touchMove = (event) => {
        this.mouseMove(event)
        this.setState({
            drag: true,
        })
    }

    mouseLeave = (event) => {
        this.setState({
            hoverTime: null,
            drag: false,
        })
    }

    touchEnd = (event) => {
        this.props.onNewTime(this.state.hoverTime)
        this.setState({
            currentTime: this.state.hoverTime,
            hoverTime: null,
            drag: false,
        })
    }

    getCurrentTime() {
        this.setState({
            currentTime: this.props.onReturnCurrentTime(),
        })
        this.timerGetCurrentTime = setTimeout(() => {
            this.getCurrentTime()
        }, 1000)
    }

    progressPercent() {
        let t = this.state.currentTime
        if ((this.state.hoverTime !== null) && this.state.drag)
            t = this.state.hoverTime
        return ((t / this.props.duration) * 100).toString() + '%'
    }

    getEventXOffset(event) {
        if (event.type.match('^touch')) {
            if (event.originalEvent)
                event = event.originalEvent
            event = event.touches[0] || event.changedTouches[0]
        }
        
        var offsetLeft = 0
        var elem = this.slider
        do {
            if (!isNaN(elem.offsetLeft)) {
                offsetLeft += elem.offsetLeft
            }
        } while(elem = elem.offsetParent)

        let x = event.clientX - offsetLeft
        if (x > this.slider.offsetWidth)
            x = this.slider.offsetWidth
        if (x < -1) 
            return 0
        return x+1
    }

    renderHoverTime() {
        if (this.state.hoverTime === null)
            return null
        return <div 
            className="hover-time" 
            style={{left: ((this.state.hoverTime / this.props.duration) * 100).toString() + '%'}}
        >
            <div className="hover-time-box">
                {secondsToTime(parseInt(this.state.hoverTime))}
            </div>
        </div>
    }

    render() {
        return (
            <div 
                className="player-slider-wrapper" 
                onClick={this.sliderClick}
                onMouseMove={this.mouseMove}
                onMouseLeave={this.mouseLeave}
                onTouchStart={this.mouseMove}
                onTouchMove={this.touchMove}
                onTouchCancel={this.mouseLeave}
                onTouchEnd={this.touchEnd}
            >
                {this.renderHoverTime()}
                <div 
                    className="slider"
                    ref={(ref) => this.slider = ref}
                >
                    <div 
                        className="progress" 
                        style={{width: this.progressPercent()}}
                    >
                    </div>
                </div>
            </div>
        )
    }
}
Slider.propTypes = propTypes

export default Slider
import React from 'react'
import PropTypes from 'prop-types'
import {secondsToTime} from 'utils'
import {request} from 'api'

import './Slider.scss'

const propTypes = {
    duration: PropTypes.number.isRequired,
    onReturnCurrentTime: PropTypes.func.isRequired,
    onNewTime: PropTypes.func.isRequired,
    playId: PropTypes.string,
    playServerUrl: PropTypes.string,
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
        this.hasThumbnails = false
    }

    componentDidMount() {
        this.getCurrentTime()
        request(`${this.props.playServerUrl}/thumbnails/1.webp?play_id=${this.props.playId}`).done(() => {
            this.hasThumbnails = true
        })
    }

    componentWillUnmount() {
        clearTimeout(this.timerGetCurrentTime)
        this.timerGetCurrentTime = null
    }

    sliderClick = (event) => {
        let t = this.state.hoverTime
        if (!t || t < 0)
            t = 0
        this.props.onNewTime(t)
        this.setState({
            currentTime: t,
            hoverTime: null,
            drag: false,
            thumbnail: null,
        })
        clearTimeout(this.thumbnailTimeout)
    }

    mouseMove = (event) => {
        if (event.type.match('^touch')) {
            if (event.originalEvent)
                event = event.originalEvent
            event = event.touches[0] || event.changedTouches[0]
        }
        let r = this.slider.getBoundingClientRect()
        const half = (this.hoverTime.offsetWidth/2)
        let x = event.clientX - r.left
        if (x < 0)
            x = 0
        let norm = this.props.duration / (r.right - r.left)
        let newTime = Math.trunc(norm*x)
        if (newTime > this.props.duration)
            newTime = this.props.duration
        this.setState({
            hoverTime: newTime,
            drag: event.buttons == 1,
        })
        
        if ((event.clientX - half) <= 0) {
            x = half-r.left
        } else if ((event.clientX + half) > window.innerWidth) {
            x = window.innerWidth - (half+(window.innerWidth-r.right))
        }
        this.hoverTime.style.left = `${x}px`
        
        clearTimeout(this.thumbnailTimeout)
        this.thumbnailTimeout = setTimeout(() => {
            this.setThumbnail()
        }, 5)
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
            thumbnail: null,
        })
    }

    touchEnd = (event) => {
        this.props.onNewTime(this.state.hoverTime)
        this.mouseLeave(event)
        this.setState({
            currentTime: this.state.hoverTime,
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
        const r = ((t / this.props.duration) * 100).toString()
        if (r > 100)
            return '100%'
        return  r+'%'
    }

    setThumbnail() {
        if (!this.hasThumbnails)
            return
        let a = (Math.round(this.state.hoverTime / 60))
        if (a < 1)
            a = 1
        this.setState({
            thumbnail: `${this.props.playServerUrl}/thumbnails/${a}.webp?play_id=${this.props.playId}`
        })
    }

    renderHoverTime() {
        return <div 
            ref={(ref) => (this.hoverTime = ref)}
            className="hover-time"
            style={{visibility:this.state.hoverTime!==null?'visible':'hidden'}}
        >
            <div>{this.state.thumbnail?<img width="240px" src={this.state.thumbnail} />: null}</div>
            <div>{secondsToTime(parseInt(this.state.hoverTime || 0))}</div>
        </div>
    }

    render() {
        return (
            <div className="slider-wrapper"
                onClick={this.sliderClick}
                onMouseMove={this.mouseMove}
                onMouseLeave={this.mouseLeave}
                onTouchStart={this.mouseMove}
                onTouchMove={this.touchMove}
                onTouchCancel={this.mouseLeave}
                onTouchEnd={this.touchEnd}
            >
                {this.renderHoverTime()}
                <div className="slider"
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
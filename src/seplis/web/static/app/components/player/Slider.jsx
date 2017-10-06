import React from 'react';
import PropTypes from 'prop-types';

import './Slider.scss';

const propTypes = {
    duration: PropTypes.number.isRequired,
    onReturnCurrentTime: PropTypes.func.isRequired,
    onNewTime: PropTypes.func.isRequired,
}

class Slider extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            currentTime: 0,
        }
        this.onSliderClick = this.sliderClick.bind(this);
        this.timerGetCurrentTime = null;
    }

    componentDidMount() {
        this.getCurrentTime();
    }

    componentWillUnmount() {
        clearTimeout(this.timerGetCurrentTime);
        this.timerGetCurrentTime = null;
    }

    sliderClick(event) {
        let x = this.getEventXOffset(event);
        let norm = this.props.duration / this.slider.offsetWidth;
        var newTime = Math.trunc(norm*x);
        this.setState({
            currentTime: newTime,
        });
        this.props.onNewTime(newTime);
    }

    getCurrentTime() {
        this.setState({
            currentTime: this.props.onReturnCurrentTime(),
        });
        this.timerGetCurrentTime = setTimeout(() => {
            this.getCurrentTime();
        }, 1000);
    }

    progressPercent() {
        return ((this.state.currentTime / this.props.duration) * 100).toString() + '%';
    }

    getEventXOffset(event) {
        if (event.type.match('^touch')) {
            event = event.originalEvent.touches[0] || 
                event.originalEvent.changedTouches[0];
        }
        
        var offsetLeft = 0;
        var elem = this.slider;
        do {
            if (!isNaN( elem.offsetLeft)) {
                offsetLeft += elem.offsetLeft;
            }
        } while(elem = elem.offsetParent);

        let x = event.clientX - offsetLeft;
        if (x > this.slider.offsetWidth)
            x = this.slider.offsetWidth;
        return x;
    }

    render() {
        return (
            <div className="player-slider-wrapper" onClick={this.onSliderClick}>
                <div 
                    className="slider"
                    ref={(ref) => this.slider = ref}
                >
                    <div 
                        className="progress" 
                        style={{width: this.progressPercent()}}
                    />
                </div>
            </div>
        )
    }
}
Slider.propTypes = propTypes;

export default Slider;
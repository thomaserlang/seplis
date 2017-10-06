import React from 'react';
import PropTypes from 'prop-types';
import ClassNames from 'classnames';

import './VolumeBar.scss';

const propTypes = {
    onChange: PropTypes.func,
}

class VolumeBar extends React.Component {

    constructor(props) {
        super(props);        
        this.onSliderMouseMove = this.sliderMouseMove.bind(this);
        this.onSliderClick = this.sliderClick.bind(this);
        this.onClick = this.click.bind(this);

        this.state = {
            percent: (localStorage.getItem('volume') || 1)*100,
            show: false,
            muted: false,
        }
        this.onDocumentClick = this.documentClick.bind(this);
    }

    componentDidMount() {
        let volume = localStorage.getItem('volume') || 1;
        if (this.props.onChange)
            this.props.onChange(volume);
        document.addEventListener('click', this.onDocumentClick);
    }

    componentWillUnmount() {
        document.removeEventListener('click', this.onDocumentClick);
    }
    
    documentClick(e) {
        if (!this.icon.contains(e.target)) {
            this.setState({show: false});
        }
    }

    sliderMouseDown(event) {
        this.sliderDrag = true;
    }

    sliderMouseMove(event) {
        if (event.buttons != 1) return;
        this.onSliderClick(event);
    }

    sliderClick(event) {
        event.preventDefault();
        event.stopPropagation();
        let scrubber = event.target.querySelector('.scrubber');
        let y = event.clientY;
        y -= event.target.offsetTop + scrubber.offsetTop;
        y = scrubber.offsetHeight - y;
        if (y > scrubber.offsetHeight)
            y = scrubber.offsetHeight;
        if (y < 0)
            y = 0;
        let norm = 1 / scrubber.offsetHeight;
        let volume = norm*y;
        if (volume < 0)
            volume = 0;
        this.setState({percent: volume*100});
        if (this.props.onChange)
            this.props.onChange(volume);
        localStorage.setItem('volume', volume);
    }

    click(event) {
        this.setState({show: !this.state.show});
    }

    renderBar() {
        if (!this.state.show) return;
        return (
            <div 
                className="volume-slider"
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
        });
        return (
            <span 
                className={volume} 
                onClick={this.onClick}
                onMouseLeave={this.onMouseLeave}
                ref={(ref) => this.icon = ref}
            >
                {this.renderBar()}
            </span>
        )
    }

}
VolumeBar.propTypes = propTypes;

export default VolumeBar;
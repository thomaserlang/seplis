import React from 'react'
import ClassNames from 'classnames'
import PropTypes from 'prop-types'
import {getVideoStream} from 'seplis/utils'

const propTypes = {
    metadata: PropTypes.object,
    onResolutionChange: PropTypes.func,
    bottom: PropTypes.bool,
}

class Resolution extends React.Component {

    constructor(props) {
        super(props)

        this.originalWidth = getVideoStream(this.props.metadata.streams).width
        this.state = {
            show: false,
            width: this.originalWidth,
        }
        
        this.resolutions = {
            7680: '8K',
            3840: '4K',
            1920: '1080p',
            1280: '720p',
            852: '480p',
            480: '360p',
            352: '144p',
        }

        this.onClick = this.click.bind(this)

        this.onResolutionClick = this.resolutionClick.bind(this)
        this.onDocumentClick = this.documentClick.bind(this)
    }

    componentDidMount() {    
        document.addEventListener('click', this.onDocumentClick)
    }

    componentWillUnmount() {
        document.removeEventListener('click', this.onDocumentClick)
    }
    
    documentClick(e) {
        if (this.icon == undefined) 
            return
        if (!this.icon.contains(e.target))
            this.setState({show: false})
    }

    click(event) {
        this.setState({show: !this.state.show})
    }

    resolutionClick(event) {
        event.preventDefault()
        this.setState(
            {
                show: false, 
                width: parseInt(event.target.getAttribute('data-width')),
            },
            () => {
                if (this.props.onResolutionChange)
                    this.props.onResolutionChange(this.state.width)
            }
        )
    }

    widthToText(width) {
        if (width in this.resolutions)
            return this.resolutions[width]
        return `W: ${width}`
    }

    renderResolutions() {
        if (!this.state.show)
            return null
        let cls = ClassNames({
            'text-box': true,
            'text-box-bottom': this.props.bottom,
        })
        return (
            <div 
                className={cls} 
            >
                {Object.entries(this.resolutions).map(([key, value]) => {
                    if (key < this.originalWidth)
                        return <p
                            key={key}
                            data-width={key}
                            onClick={this.onResolutionClick}
                        >{key==this.state.width?<b>{value}</b>:value}</p>
                })}
                <p
                    data-width={this.originalWidth}
                    onClick={this.onResolutionClick}
                >{this.originalWidth==this.state.width?<b>{this.widthToText(this.originalWidth)}</b>:this.widthToText(this.originalWidth)}</p>

            </div>
        )
    }

    render() {
        return (
            <span
                ref={(ref) => this.icon = ref}
            >
                <span 
                    onClick={this.onClick}
                    style={{'fontSize': '18px'}}
                >{this.widthToText(this.state.width)}</span>
                {this.renderResolutions()}
            </span>
        )
    }
}
Resolution.propTypes = propTypes

export default Resolution


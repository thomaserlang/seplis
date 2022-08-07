import React from 'react'
import ClassNames from 'classnames'
import PropTypes from 'prop-types'

const propTypes = {
    sources: PropTypes.array,
    selectedSource: PropTypes.object,
    onResolutionChange: PropTypes.func,
    onSelected: PropTypes.func,
}

class Resolution extends React.Component {

    constructor(props) {
        super(props)

        this.sourceWidths = []
        this.topWidth = 0
        for (const source of this.props.sources) {
            this.sourceWidths.push(source.width)
            this.topWidth = source.width
        }
        this.state = {
            width: this.props.selectedSource.width,
            source: this.props.selectedSource,
        }
        
        this.resolutions = {
            7680: '8K',
            3840: '4K',
            2560: '1440p',
            1920: '1080p',
            1280: '720p',
            852: '480p',
            480: '360p',
            352: '144p',
        }
    }
    
    onClick = () => {
        this.setState({show: !this.state.show})
    }

    onResolutionClick = (event) => {
        event.preventDefault()
        const source = this.findSource(parseInt(event.currentTarget.getAttribute('data-source-index')))
        this.setState(
            {
                show: false, 
                width: parseInt(event.currentTarget.getAttribute('data-width')),
                source: source,
            },
            () => {
                if (this.props.onSelected)
                    this.props.onSelected()
                if (this.props.onResolutionChange)
                    this.props.onResolutionChange(this.state.width, source)
            }
        )
    }

    findSource(index) {
        for (const source of this.props.sources) {
            if (source['index'] == index)
                return source
        }
    }

    widthToText(width) {
        if (width in this.resolutions)
            return this.resolutions[width]
        return `W: ${width}`
    }

    render() {
        return <div className="items">
            {Object.entries(this.resolutions).map(([key, value]) => {
                key = parseInt(key)
                if (!this.sourceWidths.includes(key) && (key < this.topWidth))
                    return <div
                        className="item"
                        key={`res-${key}`}
                        data-width={key}
                        data-source-index={this.props.sources[this.props.sources.length-1]['index']}
                        onClick={this.onResolutionClick}
                    >{key==this.state.width?<b>{value}</b>:value}</div>
            })}

            <div className="title mt-2">Sources</div>
            {this.props.sources.map(source => {
                const text = `${this.widthToText(source.width)} ${source.codec}`
                return <div 
                    key={`source-${source['index']}`}
                    data-source-index={source['index']}
                    data-width="0"
                    onClick={this.onResolutionClick}
                    className="item"
                >
                    {(this.state.source.index == source['index'])?<b>{text}</b>:text}
                </div>
            })}
        </div>
    }

}
Resolution.propTypes = propTypes

export default Resolution


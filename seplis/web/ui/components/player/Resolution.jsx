import React from 'react'
import ClassNames from 'classnames'
import PropTypes from 'prop-types'

const propTypes = {
    sources: PropTypes.array,
    selectedSource: PropTypes.object,
    onResolutionChange: PropTypes.func,
    bottom: PropTypes.bool,
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
            show: false,
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

    componentDidMount() {    
        document.addEventListener('click', this.onDocumentClick)
    }

    componentWillUnmount() {
        document.removeEventListener('click', this.onDocumentClick)
    }
    
    onDocumentClick = (e) => {
        if (this.icon == undefined) 
            return
        if (!this.icon.contains(e.target))
            this.setState({show: false})
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
                    key = parseInt(key)
                    if (!this.sourceWidths.includes(key) && (key < this.topWidth))
                        return <p
                            key={`res-${key}`}
                            data-width={key}
                            data-source-index={this.props.sources[this.props.sources.length-1]['index']}
                            onClick={this.onResolutionClick}
                        >{key==this.state.width?<b>{value}</b>:value}</p>
                })}

                <div className="title mt-2">Sources</div>
                {this.props.sources.map(source => {
                    const text = `${this.widthToText(source.width)} ${source.codec}`
                    return <p 
                        key={`source-${source['index']}`}
                        data-source-index={source['index']}
                        data-width="0"
                        onClick={this.onResolutionClick}
                    >
                        {(this.state.source.index == source['index']) && (this.state.width == this.state.source.width)?<b>{text}</b>:text}
                    </p>
                })}
            </div>
        )
    }

    render() {
        return (
            <span
                ref={(ref) => this.icon = ref}
            >
                <i                     
                    onClick={this.onClick} 
                    className="fa-solid fa-clapperboard" 
                />
                {this.renderResolutions()}
            </span>
        )
    }
}
Resolution.propTypes = propTypes

export default Resolution


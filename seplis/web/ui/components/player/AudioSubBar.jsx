import React from 'react'
import ClassNames from 'classnames'
import PropTypes from 'prop-types'

const propTypes = {
    source: PropTypes.object,
    onAudioChange: PropTypes.func,
    onSubtitleChange: PropTypes.func,
    bottom: PropTypes.bool,
}

class AudioSubBar extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            show: false,
        }
        this.onClick = this.click.bind(this)

        this.onAudioClick = this.audioClick.bind(this)
        this.onSubtitleClick = this.subtitleClick.bind(this)
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

    subtitleClick(event) {
        event.preventDefault()
        this.setState({show: false})
        if (this.props.onSubtitleChange)
            this.props.onSubtitleChange(
                event.target.getAttribute('data-data')
            )
    }

    audioClick(event) {
        event.preventDefault()
        this.setState({show: false})
        if (this.props.onAudioChange)
            this.props.onAudioChange(
                event.target.getAttribute('data-data')
            )
    }

    renderSubtitles() {
        if (this.props.source.subtitles.length == 0)
            return
        return (
            <span>
                <p className="title">Subtitles</p>
                <p><a href="#" onClick={this.onSubtitleClick} data-data="">None</a></p>
                {this.props.source.subtitles.map(l => (
                    <p key={l.index}>
                        <a 
                            href="#" 
                            onClick={this.onSubtitleClick}
                            data-data={`${l.language}:${l.index}`}
                        >
                            {l.title}
                        </a>
                    </p>
                ))}
            </span>
        )
    }

    renderAudio() {
        if (this.props.source.audio.length <= 1)
            return
        return (
            <span>
                <p className="title">Audio</p>
                {this.props.source.audio.map(l => (
                    <p key={l.index}>                        
                        <a 
                            href="#" 
                            onClick={this.onAudioClick}
                            data-data={`${l.language}:${l.index}`}
                        >
                            {l.title}
                        </a>
                    </p>
                ))}
            </span>
        )
    }

    renderAudioSubtitles() {
        if (!this.state.show)
            return null
        let cls = ClassNames({
            'text-box': true,
            'text-box-bottom': this.props.bottom,
        })
        return (
            <div 
                className={cls} 
                ref={(ref) => this.audioSubtitlesElem = ref}
            >
                {this.renderSubtitles()}
                {this.renderAudio()}
            </div>
        )
    }

    render() {
        if ((this.props.source.audio.length <= 1) && (this.props.source.subtitles.length == 0))
            return null
        return (
            <span
                ref={(ref) => this.icon = ref}
            >
                <span className="fas fa-closed-captioning" onClick={this.onClick} />
                {this.renderAudioSubtitles()}
            </span>
        )
    }
}
AudioSubBar.propTypes = propTypes

export default AudioSubBar


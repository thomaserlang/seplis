import React from 'react'
import ClassNames from 'classnames'
import PropTypes from 'prop-types'
import './AudioSubBar.scss'

const propTypes = {
    metadata: PropTypes.object,
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
        this.audio = []
        this.subtitles = []
        this.parseMetadata()

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

    parseMetadata() {
        for (let stream of this.props.metadata.streams) {
            if (!('tags' in stream))
                continue
            let lang = null
            if ('title' in stream.tags)
                lang = stream.tags.title
            if ('language' in stream.tags)
                lang =  stream.tags.language
            if (!lang)
                continue
            let s = {
                language: lang,
                title: stream.tags.title || lang,
                index: stream.index,
            }
            switch(stream.codec_type) {
                case 'subtitle': this.subtitles.push(s)
                case 'audio': this.audio.push(s)
            }
        }
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
        if (this.subtitles.length == 0)
            return
        return (
            <span>
                <p className="title">Subtitles</p>
                <p><a href="#" onClick={this.onSubtitleClick} data-data="">None</a></p>
                {this.subtitles.map(l => (
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
        if (this.audio.length <= 1)
            return
        return (
            <span>
                <p className="title">Audio</p>
                {this.audio.map(l => (
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
            'audio-subtitles': true,
            'audio-subtitles-bottom': this.props.bottom,
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
        if ((this.audio.length <= 1) && (this.subtitles.length == 0))
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


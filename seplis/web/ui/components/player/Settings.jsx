import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'
import AudioSubBar from './AudioSubBar.jsx'
import Resolution from './Resolution.jsx'

function Settings(props) {

    return <div className="overlay-box">
        <div className="close-icon" onClick={props.closeClick}><i className="fa-solid fa-xmark" /></div>
        <div className="box-group">
            <div className="title">Quaility</div>
            <Resolution 
                sources={props.sources}
                selectedSource={props.selectedSource}
                onResolutionChange={props.onResolutionChange}
                onSelected={props.closeClick}
            />
        </div>
        <div className="box-group">
            <div className="title">Audio</div>
            <SelectAudio
                audio={props.selectedSource.audio} 
                onAudioChange={props.onAudioChange}
                onSelected={props.closeClick}
            />
        </div>
        <div className="box-group">
            <div className="title">Subtitles</div>
            <SelectSubtitle 
                subtitles={props.selectedSource.subtitles}
                onSubtitleChange={props.onSubtitleChange}
                onSelected={props.closeClick}
            />
        </div>
    </div>
}

export default function SettingsIcon(props) {
    const [visible, setVisible] = useState(false)

    const onClick = () => {
        setVisible(!visible)
    }

    return <>
        <i className="fa-solid fa-gear" onClick={onClick}></i>
        <div style={{visibility: visible?'visible':'hidden'}}>
            <Settings closeClick={onClick} {...props} />
        </div>
    </>
}
SettingsIcon.propTypes = {
    sources: PropTypes.array,
    selectedSource: PropTypes.object,
    onResolutionChange: PropTypes.func,
    onAudioChange: PropTypes.func,
    onSubtitleChange: PropTypes.func,
}


function SelectAudio(props) {
    const onClick = (e) => {
        props.onSelected()
        props.onAudioChange(e.target.getAttribute('data-data'))
    }

    return <div className="items">
        {props.audio.map(l => (
            <div 
                key={`select-audio-${l.index}`}            
                onClick={onClick}
                data-data={`${l.language}:${l.index}`}
                className="item"
            >                        
                {l.title}
            </div>
        ))}
    </div>
}

function SelectSubtitle(props) {
    const onClick = (e) => {
        props.onSelected()
        props.onSubtitleChange(
            e.target.getAttribute('data-data')
        )
    }

    return <div className="items">
        <div className="item" onClick={onClick} data-data="">Off</div>
        {props.subtitles.map(l => (
            <div 
                key={`select-subtitle-${l.index}`}            
                onClick={onClick}
                data-data={`${l.language}:${l.index}`}
                className="item"
            >                        
                {l.title}
            </div>
        ))}
    </div>
}
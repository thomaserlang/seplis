import { Time, TimeSlider } from '@videojs/react'
import type { CSSProperties } from 'react'

export function PlayerTimeControls({
    timeSliderStyle,
}: {
    timeSliderStyle?: CSSProperties
}) {
    return (
        <div className="media-time-controls">
            <Time.Value type="current" className="media-time" />
            <TimeSlider.Root className="media-slider" style={timeSliderStyle}>
                <TimeSlider.Track className="media-slider__track">
                    <TimeSlider.Fill className="media-slider__fill" />
                    <TimeSlider.Buffer className="media-slider__buffer" />
                </TimeSlider.Track>
                <TimeSlider.Thumb className="media-slider__thumb" />
                <TimeSlider.Thumb className="react-time-slider-parts__thumb" />

                <div className="media-surface media-preview media-slider__preview">
                    <TimeSlider.Value
                        type="pointer"
                        className="media-time media-preview__time"
                    />
                </div>
            </TimeSlider.Root>
            <Time.Value type="duration" className="media-time" />
        </div>
    )
}

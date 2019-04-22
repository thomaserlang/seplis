import React from 'react'

class RenderError extends React.Component {
    render() {
        let error = this.props.error
        if (!error)
            return null
        if (error.errors)
            return <div className="alert alert-danger capitalize-first-letter" role="alert">
                <div className="mb-2"><b>Error:</b> {error.message}</div>
                {error.errors.map(e => (
                    <div key={e.field}><b>{e.field}:</b> {e.message}</div>
                ))}
            </div>
        return <div className="alert alert-danger capitalize-first-letter" role="alert">
            <div><b>Error:</b> {error.message}</div>
        </div>
    }
}

export default RenderError;
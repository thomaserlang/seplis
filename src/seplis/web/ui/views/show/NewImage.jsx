import React from 'react'
import {Link} from 'react-router-dom'
import {request} from 'api'
import {locationQuery, getUserLevel} from 'utils'

class NewImage extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            selectedFile: null,
        }
    }

    componentDidMount() {
        document.title = `New Image | SEPLIS`
    }

    onUpload = () => {
        let show = this.props.show 
        request(`/1/shows/${show.id}/images`, {
            data: {
                'source_title': 'User upload',
                'type': 1,
            },
        }).done((image) => {
            let fd = new FormData()
            fd.append(
                'file', 
                this.state.selectedFile, 
                this.state.selectedFile.name
            )
            request(`/1/shows/${show.id}/images/${image.id}/data`, {
                data: fd,
            }).done(() => {
                location.href = `/show/${show.id}/images`
            }).fail((e) => {
                alert(e.responseJSON.message)
            })

        }).fail((e) => {
            alert(e.responseJSON.message)
        })
    }

    onFileChange = (event) => {
        this.setState({selectedFile: event.target.files[0]})
    }

    render() {
        return <div>            
            <h3>New Image</h3>

            <div className="d-flex">
                <div>
                    <input 
                        type="file" 
                        className="form-control" 
                        onChange={this.onFileChange}
                    />
                </div>
                <div>
                    <button 
                        className="btn btn-primary ml-2"
                        onClick={this.onUpload}
                    >Upload</button>
                </div>
            </div>
        </div> 
    }

}

export default NewImage 
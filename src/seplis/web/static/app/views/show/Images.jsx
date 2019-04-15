import React from 'react'
import {request} from 'api'
import Loader from 'components/Loader'
import Pagination from 'components/Pagination'
import {locationQuery, getUserLevel} from 'utils'

class Images extends React.Component {
    
    constructor(props) {
        super(props)
        this.state = {
            images: null,
            loading: true,
            jqXHR: null,
            page: locationQuery().page || 1,
        }
    }

    componentDidMount() {
        this.get()
    }

    componentDidUpdate(prevProps) {
        if (this.props.location !== prevProps.location) {
            this.setState({
                page: locationQuery().page || 1,
                loading: true,
            },() => {
                this.get()
            })
        }
    }

    setBrowserPath() {
        this.props.history.push(`${this.props.location.pathname}?page=${this.state.page}`)
    }

    pageChange = (e) => {
        this.setState({
            page: e.target.value,
            loading: true,
        }, () => {
            this.setBrowserPath()
            this.get()
        })
    }

    get() {
        let show = this.props.show
        request(`/1/shows/${show.id}/images`, {
            query: {
                page: this.state.page,
                per_page: 8,
            }
        }).done(
            (data, textStatus, jqXHR) => {
                this.setState({
                    images: data,
                    jqXHR: jqXHR,
                    loading: false,
                })
            }
        )
    }

    setDefault = (e) => {
        e.preventDefault()
        let show = this.props.show        
        request(`/1/shows/${show.id}`, {
            data: {
                poster_image_id: e.target.getAttribute('image-id')
            },
            method: 'PUT',
        }).done(() => {
            location.reload()
        }).fail((e) => {
            alert(e.message)
        })
    }

    renderSetDefault(image) {
        if (getUserLevel() < 2)
            return
        let pi = this.props.show.poster_image
        if (pi && (pi.hash == image.hash)) 
            return <div className="black-box">
                Is Default
            </div>
        return <div className="black-box">
            <a href="#" image-id={image.id} onClick={this.setDefault}>
                Set as Default
            </a>
        </div>
    }

    render() {
        if (this.state.loading)
            return <Loader />

        return <> 
            <div className="row">
                {this.state.images.map(i => (
                    <div key={i.hash} className="col-1 col-sm-3 col-margin">
                        <a href={i.url+'@.jpg'} target="_blank">
                        <img 
                            title={this.props.show.title}
                            alt={this.props.show.title}
                            src={i.url + '@SX180'}
                            className="img-fluid" 
                        />
                        </a>
                        {this.renderSetDefault(i)}
                    </div>
                ))}
            </div>

            <div className="row">
                <div className="col-12 col-sm-9 col-md-10">
                </div>
                <div className="col-sm-3 col-md-2">
                    <Pagination 
                        jqXHR={this.state.jqXHR} 
                        onPageChange={this.pageChange}
                    />
                </div>
            </div>
        </>
    }
}

export default Images
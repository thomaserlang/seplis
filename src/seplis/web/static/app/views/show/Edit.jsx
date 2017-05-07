import React from 'react';
import EditFields from 'components/shows/EditFields';
import Serialize from 'form-serialize';
import {unflatten} from 'flat';
import {request} from 'api';

const propTypes = {
    show: React.PropTypes.object,
}

class Edit extends React.Component {

    constructor(props) {
        super(props);
        this.onSubmit = this.submit.bind(this);
        this.state = {
            error: null,
            success: null,
            loading: false,
        }
    }

    submit(e) {
        e.preventDefault();
        this.setState({
            success: null,
            error: null,
            loading: true,
        })
        let data = unflatten(
            Serialize(e.target, {hash: true})
        );
        request(`/1/shows/${this.props.show.id}`, {
            data: data,
            method: 'PUT',
        }).success(show => {
            this.setState({success: show});
            request(`/1/shows/${this.props.show.id}/update`, {
                method: 'POST',
            });
        }).error(e => {
            this.setState({error: e.responseJSON});
        }).always(() => {
            this.setState({loading: false});
        });
    }

    renderError() {
        if (!this.state.error) return '';
        return (
            <div className="alert alert-danger">
                {this.state.error.message}
            </div>
        )
    }

    renderSuccess() {
        if (!this.state.success) return '';
        return (
            <div className="alert alert-success">
                The show was successfully updated.
            </div>
        )
    }

    render() {
        return (
            <form method="post" onSubmit={this.onSubmit}>
                <EditFields show={this.props.show} />
                {this.renderError()}
                {this.renderSuccess()}
                <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={this.state.loading}
                >
                    {this.state.loading?'Saving...':'Save'}
                </button>
            </form>
        )
    }
}
Edit.propTypes = propTypes;

export default Edit;
import React from 'react';

class SignOut extends React.Component {

    componentDidMount() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('accessLevel');
        location.href = '/sign-in';
    }

    render() {
        return null;
    }
}

export default SignOut;
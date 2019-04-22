import React from 'react'
import ReactDOM from 'react-dom'

import {BrowserRouter, Switch, Route} from "react-router-dom"

import Index from './views/'
import SignIn from './views/SignIn'
import SignOut from './views/SignOut'
import CreateUser from './views/CreateUser'
import PlayEpisode from './views/show/PlayEpisode'
import ResetPassword from './views/ResetPassword'

import './styles/Base.scss'
import './styles/FormBase.scss'

import {apiClientSettings} from './api.jsx'
import Chromecast from 'components/player/Chromecast'

ReactDOM.render((
    <BrowserRouter>
        <Switch>
            <Route exact path="/sign-in" component={SignIn} />
            <Route exact path="/sign-out" component={SignOut} />
            <Route exact path="/create-user" component={CreateUser} />
            <Route exact path="/reset-password" component={ResetPassword} />
            <Route path="/reset-password/:key" component={ResetPassword} />
            <Route exact path="/show/:showId/episode/:number/play" component={PlayEpisode} />
            <Route path="/" component={Index} />            
        </Switch>
    </BrowserRouter>
), document.getElementById('root'))
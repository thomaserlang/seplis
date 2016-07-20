import React from 'react';
import {Router, Route, browserHistory, IndexRedirect} from 'react-router';

import Show from './views/show/Show';
import ShowMain from './views/show/Main';
import ShowSeasons from './views/show/Seasons';
import ShowInfo from './views/show/Info';
import ShowEdit from './views/show/Edit';

import ShowNew from './views/show/New';

export default (
    <Router history={browserHistory}>
        <Route path="/show/:showId" component={Show}>
            <IndexRedirect to="/show/:showId/main" />
            <Route path="main" component={ShowMain} />
            <Route path="info" component={ShowInfo} />
            <Route path="seasons" component={ShowSeasons} />
            <Route path="edit" component={ShowEdit} />
        </Route>
        <Route path="/show-new" component={ShowNew} />
    </Router>
);
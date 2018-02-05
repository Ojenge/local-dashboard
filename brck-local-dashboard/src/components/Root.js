import React, {Component} from 'react';

import {
    BrowserRouter as Router,
    Route,
    Redirect
} from 'react-router-dom';

import Dashboard from './Dashboard';
import Connections from './Connections';
import Login from './Login';
import Logout from './Logout';
import Boot from './Boot';
import Auth from '../utils/Auth';


const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route {...rest} render={props => (
    Auth.isAuthenticated() ? (
      <Component {...props}/>
    ) : (
      <Redirect to={{
        pathname: '/login',
        state: { from: props.location }
      }}/>
    )
  )}/>
)


class Root extends Component {

  render() {
    return (
      <Router>
        <div>
          <Route exact path="/" component={ Boot } />
          <Route exact path="/login" component={ Login } />
          <PrivateRoute exact path="/logout" component={ Logout } />
          <PrivateRoute exact path='/dashboard' component={ Dashboard } />
          <PrivateRoute exact path='/connect' component={ Connections } />
        </div>
    </Router>
    );
  }
}


export default Root;
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
import ChangePassword from './ChangePassword';
import Power from './Power';
import Auth from '../utils/Auth';


const PrivateRoute = ({ component: Component, ...rest }) => {
  const show_change = (Component.name !== 'ChangePassword') && Auth.requiresPasswordChange();
  return (
    <Route {...rest} render={props => (
      Auth.isAuthenticated() ? (
        show_change ? (
          <Redirect to={{
            pathname: '/change-password',
            state: { from: props.location }
          }}/>
        ) : (
          <Component {...props}/>
        )
      ) : (
        <Redirect to={{
          pathname: '/login',
          state: { from: props.location }
        }}/>
      )
    )}/>
  );
}


class Root extends Component {

  render() {
    return (
      <Router>
        <div>
          <Route exact path="/" component={ Boot } />
          <Route exact path="/login" component={ Login } />
          <PrivateRoute exact path="/change-password" component={ ChangePassword } />
          <PrivateRoute exact path="/logout" component={ Logout } />
          <PrivateRoute exact path='/dashboard' component={ Dashboard } />
          <PrivateRoute exact path='/connect' component={ Connections } />
          <PrivateRoute exact path='/power' component={ Power } />
        </div>
    </Router>
    );
  }
}


export default Root;
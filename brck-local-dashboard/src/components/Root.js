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
import Software from './Software';
import Diagnostics from './Diagnostics';

const CHANGE_PASSWORD_PATH = '/change-password';

const PrivateRoute = ({ component: Component, ...rest }) => {
  const forcePassChange = (window.location.pathname !== CHANGE_PASSWORD_PATH) && Auth.requiresPasswordChange();
  if (forcePassChange) {
    window.location = CHANGE_PASSWORD_PATH;
  }
  return (
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
  );
}


class Root extends Component {

  render() {
    return (
      <Router>
        <div className={"innerRoot"}>
          <Route exact path="/" component={ Boot } />
          <Route exact path="/login" component={ Login } />
          <PrivateRoute exact path={CHANGE_PASSWORD_PATH} component={ ChangePassword } />
          <PrivateRoute exact path="/logout" component={ Logout } />
          <PrivateRoute exact path='/dashboard' component={ Dashboard } />
          <PrivateRoute exact path='/connect' component={ Connections } />
          <PrivateRoute exact path='/power' component={ Power } />
          <PrivateRoute exact path='/about' component = { Software } />
          <PrivateRoute exact path='/diagnostics' component = { Diagnostics } />
        </div>
    </Router>
    );
  }
}


export default Root;
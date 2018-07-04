import React, {Component} from 'react';

import {
    BrowserRouter as Router,
    Route,
    Redirect
} from 'react-router-dom';

import API from '../utils/API';
import Dashboard from './Dashboard';
import SIMConnectionsContainer from './SIMContainer'
import EthernetContainer from './EthernetContainer'
import Connections from './Connections'
import WIFI from './WIFI';
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
  document.body.classList.remove('sidebar-open');
  const forcePassChange = (window.location.pathname !== CHANGE_PASSWORD_PATH) && Auth.requiresPasswordChange() && Auth.isAuthenticated();
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
  constructor(props) {
    super(props);
      this.state = {
        retailMode: 1
      }
  }

  setDeviceMode = (err, res) => {
    if (res.ok){
      var retail;
      if (res.body.mode == "RETAIL"){
        retail = 1;
      } else {
        retail = 0;
      }
      this.setState({
        retailMode: retail
      });

    }
  }

  componentDidMount(){
    API.get_device_mode(this.setDeviceMode);
  }

  renderRetailRoutes = () => {
    return (
      <div style={{height: "100%"}}>
      <PrivateRoute exact path='/connect-all' component={ Connections } />
      <PrivateRoute exact path='/about' component = { Software } />
      </div>
    );
  }

  renderAdvancedRoutes = () => {
    return (
      <div>
      <PrivateRoute exact path='/connect-sim' component={ SIMConnectionsContainer } />
      <PrivateRoute exact path='/connect-lan' component={ EthernetContainer } />
      <PrivateRoute exact path='/connect-wifi' component={ WIFI } />
      <PrivateRoute exact path='/power' component={ Power } />
      <PrivateRoute exact path='/about' component = { Software } />
      <PrivateRoute exact path='/diagnostics' component = { Diagnostics } />
      </div>
    );
  }

  render() {
    return (
      <Router>
        <div className={"innerRoot"}>
          <Route exact path="/" component={ Boot } />
          <Route exact path="/login" component={ Login } />
          <PrivateRoute exact path={CHANGE_PASSWORD_PATH} component={ ChangePassword } />
          <PrivateRoute exact path="/logout" component={ Logout } />
          <PrivateRoute exact path='/dashboard' component={ Dashboard } />
          {(this.state.retailMode)
          ? this.renderRetailRoutes()
          : this.renderAdvancedRoutes() }
        </div>
      </Router>  
    );
  }
}

export default Root;

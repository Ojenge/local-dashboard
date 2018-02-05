import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';

import Auth from '../utils/Auth';

class Logout extends Component {

  render() {
    Auth.clearCredentials();
    return <Redirect to='/' />
  }

}

export default Logout;
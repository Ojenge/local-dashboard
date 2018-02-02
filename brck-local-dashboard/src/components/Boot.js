import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';

import Loading from './Loading';

import API from '../utils/API';

class Boot extends Component {

  constructor(props) {
    console.log('booting');
    super(props);
    this.state = {
      connected: false,
      counter: 0
    }
  }

  checker = () => {
    API.ping(this.handleResult);
  }

  handleResult = (err, res) => {
    var _counter = this.state.counter + 1;
    this.setState({
      counter: _counter
    });
    if (err || !res.ok) {
      console.log(err);
    } else {
      this.clearTick();
      this.setState({
        connected: true
      });
    }
  }

  componentWillMount() {
    document.body.classList.add('login-page');
}

  componentDidMount() {
    this.checker();
    this.tick = window.setInterval(this.checker, 10000);
  }

  componentWillUnmount() {
    this.clearTick();
    document.body.classList.remove('login-page');
  }

  clearTick = () => {
    if (this.tick) {
      window.clearInterval(this.tick);
    }
  }

  render() {
    return (
      this.state.connected
        ? <Redirect to='/dashboard' />
        : <Loading message={"Trying to connect to your SupaBRCK"} />
    );
  }

}

export default Boot;

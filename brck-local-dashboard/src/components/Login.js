import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';

import Logo from '../media/yellow-brck-logo.svg';

import API from '../utils/API';
import Auth from '../utils/Auth';

class Login extends Component {

    constructor(props) {
        super(props);
        this.state = {
            login: '',
            password: '',
            login_error: false,
            working: false,
            authenticated: false
        }
    }

    componentWillMount() {
        document.body.classList.add('login-page');
    }

    componentWillUnmount() {
        document.body.classList.remove('login-page');
    }

    signIn = (e) => {
        e.preventDefault();
        var _login = this.state.login;
        var _password = this.state.password;
        if (_login.length && _password.length){
          this.setState({ working: true });
          var payload = {login: _login,
                         password: _password};
          API.auth(payload, this.loginCallback);
        } else {
          this.setState({ login_error: true });
        }
    }

    loginCallback = (err, res) => {
        this.setState({ working: false });
        if (err || !res.ok) {
            this.setState({
                login_error: true,
                login_error_message: res.body.message
            });
        } else {
            var token = res.body.token;
            Auth.storeCredentials(token, res.body.password_changed);
            this.setState({
                authenticated: true
            });
        }
    }

    handleInput = (e) => {
        var xKey = e.target.name;
        var newState = {login_error: false};
        newState[xKey] = e.target.value;
        this.setState(newState);
    }

    handleKeyDown = (e) => {
      if (e.keyCode === 13) {
        this.signIn(e);
      }
    }

    renderWorking = () => {
      return (
        <div className="login-box">
                <div className="login-logo">
                </div>
                <div>
                  <div className="spinner-yellow">
                    <span />
                  </div>
                </div>
        </div>
      )
    }

    renderForm = () => {
        return (
            <div className="login-box">
                <div className="login-logo">
                    <a href="/">
                        <img src={Logo} alt="BRCK" />
                    </a>
                </div>
                <div className="login-box-body">
                    <p className="login-box-msg">Sign in to start your session</p>
        {this.state.login_error ? <p className=" login-box-msg text-red">{ this.state.login_error_message }</p> : null }

                    <form action="." method="post">
                    <div className={"form-group has-feedback" + (this.state.login_error ? " has-error" : "") }>
                        <input name="login" type="text" className="form-control" placeholder="Login"
                            autoFocus={1}
                            value={ this.state.login }
                            onChange={this.handleInput} />
                        <span className="glyphicon glyphicon-user form-control-feedback"></span>
                    </div>
                    <div className={"form-group has-feedback" + (this.state.login_error ? " has-error" : "") }>
                        <input type="password" name="password" className="form-control" placeholder="Password"
                            value={this.state.password}
                            onChange={ this.handleInput }
                            onKeyDown={ this.handleKeyDown } />
                        <span className="glyphicon glyphicon-lock form-control-feedback"></span>
                    </div>
                    <div className="row">
                        <div className="col-xs-8">
                        </div>
                        <div className="col-xs-4">
                        <a href="." className="btn btn-primary btn-block btn-flat"
                            onClick={this.signIn}>Sign In</a>
                        </div>
                    </div>
                    </form>
                </div>
            </div>
        );
    }

    render() {
        const { from } = this.props.location.state || { from: { pathname: '/' } }
        const { authenticated } = this.state;
        if (authenticated) {
          return (
            <Redirect to={from} />
          );
        }
        return (this.state.working)
                ? this.renderWorking()
                : this.renderForm();
    }

}

export default Login;
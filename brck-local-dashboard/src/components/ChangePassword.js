import React, { Component } from 'react';
import { Redirect, Link } from 'react-router-dom';

import Logo from '../media/yellow-brck-logo.svg';

import API from '../utils/API';
import Auth from '../utils/Auth';

class ChangePassword extends Component {

    constructor(props) {
        super(props);
        this.state = {
            current_password: '',
            password: '',
            password_confirmation: '',
            login_error: false,
            working: false,
            errors: {},
            completed: false
        }
    }

    componentWillMount() {
        document.body.classList.add('login-page');
    }

    componentWillUnmount() {
        document.body.classList.remove('login-page');
    }

    changePassword = (e) => {
        e.preventDefault();
        var _current_password = this.state.current_password;
        var _password = this.state.password;
        var _confirmation = this.state.password_confirmation;
        if (_current_password.length && _password.length && _confirmation.length){
          this.setState({ working: true });
          var payload = {current_password: _current_password,
                         password: _password,
                         password_confirmation: _confirmation};
          API.change_password(payload, this.authCallback);
        } else {
          this.setState({ login_error: true });
        }
    }

    authCallback = (err, res) => {
        this.setState({ working: false });
        if (err || !res.ok) {
            this.setState({
                login_error: true,
                errors: res.body.errors || {}
            });
        } else {
            Auth.setPasswordStatus(true);
            this.setState({
                completed: true
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
        this.changePassword(e);
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
                    <p className="login-box-msg">You must change your password</p>

                    <form action="." method="post">
                      <div className={"form-group has-feedback" + (this.state.login_error ? " has-error" : "") }>
                          <input name="current_password" type="password" className="form-control" placeholder="Current Password"
                              autoFocus={1}
                              value={ this.state.current_password }
                              onChange={this.handleInput} />
                          { this.state.errors.current_password ? <span className="help-block">{ this.state.errors.current_password }</span> : null }
                          <span className="glyphicon glyphicon-lock form-control-feedback"></span>
                      </div>
                      <div className={"form-group has-feedback" + (this.state.login_error ? " has-error" : "") }>
                          <input name="password" type="password" className="form-control" placeholder="New Password"
                              autoFocus={1}
                              value={ this.state.password }
                              onChange={this.handleInput} />
                          { this.state.errors.password ? <span className="help-block">{ this.state.errors.password }</span> : null }
                          <span className="glyphicon glyphicon-lock form-control-feedback"></span>
                      </div>
                      <div className={"form-group has-feedback" + (this.state.login_error ? " has-error" : "") }>
                          <input name="password_confirmation" type="password" className="form-control" placeholder="Confirm Password"
                              autoFocus={1}
                              value={ this.state.password_confirmation }
                              onChange={this.handleInput} />
                          { this.state.errors.password_confirmation ? <span className="help-block">{ this.state.errors.password_confirmation }</span> : null }
                          <span className="glyphicon glyphicon-lock form-control-feedback"></span>
                      </div>
                      <div className="row">
                          <div className="col-xs-12">
                          <a href="." className="btn btn-primary btn-block btn-flat"
                              onClick={this.changePassword}>Change Password</a>
                          { Auth.requiresPasswordChange() ? (
                            null
                          ):(
                            <Link 
                              className="btn btn-block btn-default btn-flat"
                              to="/">
                              Cancel
                            </Link>
                          )}
                          </div>
                      </div>
                    </form>
                </div>
            </div>
        );
    }

    render() {
        const { from } = this.props.location.state || { from: { pathname: '/' } }
        const { completed } = this.state;
        if (completed) {
          return (
            <Redirect to={from} />
          );
        }
        return (this.state.working)
                ? this.renderWorking()
                : this.renderForm();
    }

}

export default ChangePassword;
import React, { Component } from 'react';

import {AlertError,
        AlertSuccess} from './Alerts';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

var Humanize = require('humanize-plus');


class Storage extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      errors: {}
    }
  }

  componentDidMount() {
    this.loadState();
  }

  loadState = (live) => {
    if (!this.state.working) {
      this.setState({ working: true });
      API.get_storage(this.dataCallback);
    }
  }

  dataCallback = (res) => {
    this.setState({ working: false });
    if (!res.ok) {
      this.setState({
        loaded: false,
        net_error: true
      });
    } else {
      this.setState(res.body);
      this.setState({
        loaded: true
      });
    }
  }

  getStorageUsage = () => {
    if (this.state.storage_usage === undefined) {
      var usage = (this.state.storage.used_space / 
                   this.state.storage.total_space) * 100;
      if (isNaN(usage)) {
        usage = 0;
      }
      this.setState({
        storage_usage: usage
      });
    }
    return Humanize.formatNumber(this.state.storage_usage, 2);
  }

  handleInput = (e) => {
    var newState = {};
    newState[e.target.name] = e.target.value;
    this.setState(newState);
  }

  
  handleConfigureFTP = (e) => {
    e.preventDefault();
    var payload = {
      login: this.state.login,
      password: this.state.password
    }
    this.setState({ working: true });
    API.configure_ftp(payload, this.configCallback);
  }

  configCallback = (res) => {
    this.setState({ working: false });
    if (!res.ok) {
        var errors = (res.status === 422) ? res.body.errors : {};
        this.setState({
            config_error: true,
            errors: errors
        });
    } else {
        this.setState({
            config_saved: true,
            config_error: false,
            errors: {},
            login: '',
            password: ''
        });
        this.setState(res.body);
    }
  }

  renderStorage = () => {
    return (
      <div className="row">
        <div className="col-md-12 col-xs-12 col-lg-6">
        <div className="box">
          <div className="box-header with-border">
            <h3 className="box-title">Storage</h3>
          </div>
          <div className="box-body">
            <p>Your SupaBRCK has <span className="text-bold text-orange">
              { Humanize.fileSize(this.state.storage.total_space) }</span> of storage available 
              <span className="text-bold">({ Humanize.fileSize(this.state.storage.used_space) } - { this.getStorageUsage() }% used).</span>
            </p>
            <div className="progress">
                  <div className="progress-bar progress-bar-yellow"
                    role="progressbar"
                    aria-valuenow={ this.getStorageUsage() } 
                    aria-valuemin="0"
                    aria-valuemax="100" 
                    style={{ width: this.getStorageUsage() + '%' }}>
                      <span className="sr-only">{ this.getStorageUsage() }% used</span>
                    </div> 
              </div>
          </div>
        </div>
      </div>
    </div>
    );
  }
  renderFTPForm = () => {
    return (
      <div className="row" key="ftp-form">
        <div className="col-xs-12 col-lg-6 col-md-6">
          <div className="box box-primary">
            <div className="box-header with-border">
              <h3 className="box-title">FTP Configuration</h3>
            </div>
            <form role="form">
              <div className="box-body">
                <p>
                  This will configure access to the FTP server at <strong>local.brck.com</strong>
                </p>
                <div className={'form-group' + ' ' + (this.state.errors.login ? 'has-error' : '') }>
                    <label for="ftpLogin">Username</label>
                    <input onChange={this.handleInput} name="login" id="login" type="text" className="form-control" id="ftpLogin" placeholder="Username" />
                    {this.state.errors.login ? <span className="help-block">{ this.state.errors.login }</span> : null}
                </div>
                <div className={'form-group' + ' ' + (this.state.errors.password ? 'has-error' : '') }>
                    <label for="ftpPassword">Password</label>
                    <input onChange={this.handleInput} name="password" type="password" className="form-control" id="ftpPassword" placeholder="Password" />
                    {this.state.errors.password ? <span className="help-block">{ this.state.errors.password }</span> : null}
                    </div>
                </div>
              <div className="box-footer">
                <button onClick={this.handleConfigureFTP} type="submit" className="btn btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
     </div>
    );
  }

  renderFTPAccess = () => {
    return (
      <div className="row">
        <div className="col-md-6">
          <div className="box box-solid">
            <div className="box-header with-border">
              <h3 className="box-title">Accessing Files</h3>
            </div>
            <div className="box-body">
              <a target="_blank" href="http://local.brck.com/www" class="btn btn-block btn-social bg-navy">
                  <i class="fa fa-folder"></i> Access uploaded files
              </a>
            </div>
            <div>
          </div>
        </div>
      </div>
    </div>
    );
  }

  renderMessages = () => {
    return (
      <div className="row">
        <div className="col-xs-12">
          {(this.state.config_saved
            ? <AlertSuccess message={"Your FTP settings have been saved successfully."} />
            : null)}
          {(this.state.config_error
            ? <AlertError title={"Could not configure FTP settings"}
                errors={[]} />
            : null)}
        </div>
      </div>
    )
  }


  renderBody = () => {
    return (
      <div className="content container-fluid">
        { this.renderStorage() }
        { this.renderMessages() }
        { this.renderFTPForm()  }
        { this.renderFTPAccess() }
      </div>
    );
  }

  render() {
    return (
      <Container>
        <div>
          <Header>Content</Header>
          {(this.state.loaded)
          ? this.renderBody()
          : <Loading message="Loading storage status" />}
        </div>
      </Container>
    );
  }
}

export default Storage;
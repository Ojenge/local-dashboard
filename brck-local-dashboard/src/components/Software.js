import React, { Component } from 'react';

import { AlertError } from './Alerts';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

class Software extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      retailMode: 1
    }
  }

  componentDidMount() {
    API.get_device_mode(this.setDeviceMode);
    this.loadState();
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

  loadState = () => {
    API.get_software_state(this.dataCallback);
  }

  dataCallback = (res) => {
    if (!res.ok) {
      this.setState({
        loaded: false,
        net_error: true
      });
    } else {
      this.setState({
        software: res.body,
        loaded: true
      });
    }
  }

  renderMessages = () => {
    const rootError = "Failed to load device state"
    return (
      <div className="row">
        <div className="col-xs-12">
          {(this.state.net_error
            ? <AlertError title={"Error"}
                errors={[ rootError ]} />
            : null)}
        </div>
      </div>
    )
  }

  renderSoftwarePackages = () => {
    return (
        <div class="box">
          <div class="box-header">
            <h3 class="box-title">Software Packages</h3>
          </div>
          <div class="box-body table-responsive no-padding">
            <table class="table table-hover">
              <tbody>
                <tr>
                  <th>Package Name</th>
                  <th>Version</th>
                </tr>
                {this.state.software.packages.map(function(pkg, index) {
                  return (
                    <tr key={ "opkg-id-"+ index }>
                      <td>{ pkg.name }</td>
                      <td>{ pkg.installed ? <span>{ pkg.version }</span> : <span className="label label-danger">NOT INSTALLED</span> }</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>      
    );
  }   

  renderBody = () => {
    return (
      <div className="content container-fluid">
        { this.renderMessages() }
        <div className="row">
          <div className="col-md-12">
            <div class="box">
              <div class="box-header">
                <h3 class="box-title">System</h3>
              </div>
              <div class="box-body table-responsive no-padding">
                <table class="table table-hover">
                  <tbody>
                    <tr>
                      <td>Operating System Version</td>
                      <td>{ this.state.software.os }</td>
                    </tr>
                    <tr>
                      <td>Firmware Version</td>
                      <td>{ this.state.software.firmware }</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            {(this.state.retailMode)
             ? null
             : this.renderSoftwarePackages() }
          </div>
        </div>
      </div>
    );
  }

  render() {
    return (
      <Container>
        <div>
          <Header>About</Header>
          {(this.state.loaded)
          ? this.renderBody()
          : <Loading message="Loading device status" />}
        </div>
      </Container>
    );
  }
}

export default Software;

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
      loaded: false
    }
  }

  componentDidMount() {
    this.loadState();
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

            <div class="box">
              <div class="box-header">
                <h3 class="box-title">Packages</h3>
              </div>
              <div class="box-body table-responsive no-padding">
                <table class="table table-hover">
                  <tbody>
                    {this.state.software.packages.map(function(pkg, index) {
                      return (
                        <tr key={ "opkg-id-"+ index }>
                          <td>{ pkg.name }</td>
                          <td>{ pkg.installed ? <span className="badge bg-green">{ pkg.version }</span> : <span className="badge bg-red">not installed</span> }</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
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
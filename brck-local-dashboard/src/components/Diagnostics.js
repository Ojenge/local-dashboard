import React, { Component } from 'react';
import io from 'socket.io-client';

import { AlertError, AlertWarning } from './Alerts';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

var Humanize = require('humanize-plus');
var moment = require('moment');

const UNKNOWN = 'UNKNOWN';

class Diagnostics extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      use_degrees: true
    }
  }

  componentDidMount () {
    this.loadState();
    this.initializeSocket();
  }

  componentWillUnmount () {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  initializeSocket = () => {
    const opts = {
      transportOptions: {
        polling: {
          extraHeaders: API.getAuthHeaders()
        },
        timeout: 5000
      }
    };
    this.socket = io('/diagnostics', opts);
    this.socket.on('diagnostics', (data) => {
      this.setState({
        diagnostics: data
      });
    }); 
  }

  loadState = () => {
    API.get_diagnostic_data(this.dataCallback);
  }

  dataCallback = (res) => {
    if (!res.ok) {
      this.setState({
        loaded: false,
        net_error: true
      });
    } else {
      this.setState({
        diagnostics: res.body,
        loaded: true
      });
    }
  }

  renderMessages = () => {
    const rootError = "Failed to load diagnostic data"
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

  switchTemperatureUnit = (e) => {
    e.preventDefault();
    this.setState({
      use_degrees: !this.state.use_degrees
    });
  }

  renderTemperature = (temp, index) => {
      var _temp = temp;
      var _suffix = '\u00B0C';
      if (temp !== UNKNOWN) {
        if (!this.state.use_degrees) {
          _temp = (temp * 1.8) + 32;
          _suffix = '\u00B0F';
        }  
        _temp = Humanize.formatNumber(_temp, 2);
        _temp += _suffix;
      }
      return <span key={ 'temp-key-' + index } className="badge bg-gray">{ _temp }</span>;
  }

  renderBody = () => {
    const { diagnostics } = this.state;
    return (
      <div className="content container-fluid">
        { this.renderMessages() }
        <div className="row">
          <div className="col-md-12">
            <div class="box">
              <div class="box-header">
                <h3 class="box-title">Temperature</h3>
                <div className="box-tools">
                  <div className="input-group input-group-sm" style={{ width: '150px' }}>
                    <div className="input-group-btn">
                      <button onClick={ this.switchTemperatureUnit } className="btn btn-default btn-flat pull-right">
                        <i className="fa fa-toggle-off"/> { this.state.use_degrees ? <span>&deg;F</span> : <span>&deg;C</span> }
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="box-body table-responsive no-padding">
                <table class="table table-hover">
                  <tbody>
                    <tr>
                      <td>CPU</td>
                      <td>{ diagnostics.cpu.temperature.map(this.renderTemperature) }</td>
                    </tr>
                    <tr>
                      <td>Modem</td>
                      <td>{ diagnostics.modem.temperature.map(this.renderTemperature) }</td>
                    </tr>
                    <tr>
                      <td>Battery</td>
                      <td>{ diagnostics.battery.temperature.map(this.renderTemperature) }</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="box">
              <div class="box-header">
                <h3 class="box-title">Connected Clients</h3>
              </div>
              <div class="box-body table-responsive no-padding">
                {(diagnostics.clients === [])
                ?(
                  <AlertWarning message={"No clients connected"} />
                )
                : (
                  <table class="table table-hover">
                    <tbody>
                      <tr>
                        <th>Name</th>
                        <th>IP</th>
                        <th>Signal</th>
                        <th>Uptime</th>
                        <th>Upload</th>
                        <th>Download</th>
                      </tr>
                      {diagnostics.clients.map(function(c, index) {
                        return (
                          <tr key={ "wifi-client-id-"+ index }>
                            <td>{ c.name }</td>
                            <td>{ c.ip }</td>
                            <td>{ c.signal }</td>
                            <td>{ moment.duration(c.connected_time, 'seconds').humanize() }</td>
                            <td>{ Humanize.fileSize(c.tx_bytes) }</td>
                            <td>{ Humanize.fileSize(c.rx_bytes) }</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
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
          <Header>Diagnostics</Header>
          {(this.state.loaded)
          ? this.renderBody()
          : <Loading message="Loading device diagnostics" />}
        </div>
      </Container>
    );
  }
}

export default Diagnostics;
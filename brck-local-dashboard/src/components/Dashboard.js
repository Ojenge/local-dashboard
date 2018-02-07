import React, { Component } from 'react';
import io from 'socket.io-client';

import Loading from './Loading';
import Container from './Container';
import Header from './Header';
import API from '../utils/API';

import IconNoConnection from '../media/icons/icon_ethernet-white.svg';
import IconEthernet from '../media/icons/icon_ethernet-white.svg';
import IconSIM from '../media/icons/icon-sim.svg';


var Humanize = require('humanize-plus');

class Dashboard extends Component {

  constructor(props) {
    super(props);
    this.state = {
      connected: false,
      loading: false,
      net_error: false,
      has_data: false
    }
  }

  componentDidMount() {
    API.ping(this.connectionCallback);
    this.initializeSocket();
  }

  componentWillUnmount() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  initializeSocket = () => {
    this.socket = io('/dashboard');
    this.socket.on('system', (data) => {
      console.log("Receive data", data);
      this.setState({
        system: data
      });
    });
  }

  connectionCallback = (err, res) => {
    if (err || !res.ok){
      this.setState({
        connected: false,
        net_error: true
      });
    } else {
      this.setState({
        connected: true
      });
      API.get_system(this.systemCallback);
    }
  }

  systemCallback = (err, res) => {
    if(err || !res.ok) {
      this.setState({
        net_error: true
      });
      API.handle_error(res.status);
    } else {
      this.setState({ 
        system: res.body,
        has_data: true
      });
    }
  }

  renderBatteryInfo = (level) => {
    var containerClass = "info-box-icon bg-green";
    var levelTag = Math.round(level / 25);
    if (level === 100) {
      levelTag = 3;
    }
    if (levelTag <= 1) {
      containerClass = "info-box-icon bg-red";
    }
    var iconClass = "fa fa-battery-" + levelTag + " big-icon";
    return (
      <span className={containerClass}>
        <i className={iconClass} />
      </span>
    );
  }

  humanizeSpeed = (speed_in_bits) => {
    // Humanize plus acts on file size with a minimum size of bytes
    var humanizeBits = speed_in_bits * 8;
    var speedStr = Humanize.fileSize(humanizeBits).toLowerCase();
    return Humanize.titleCase(speedStr) + '/s';
  }

  getStorageUsage = () => {
    if (this.state.storage_usage === undefined) {
      var usage = (this.state.system.storage.used_space / 
                   this.state.system.storage.total_space) * 100;
      if (isNaN(usage)) {
        usage = 0;
      }
      this.setState({
        storage_usage: usage
      });
    }
    return this.state.storage_usage;
  }

  renderLogo = (connType) => {
    var icon = IconNoConnection;
    var _conn = this.state.system.network.connection.connection_type;
    if (_conn === 'LAN'){
      icon = IconEthernet;
    } else if (_conn === 'WAN') {
      icon = IconSIM;
    }
    return icon;
  }

  renderBody = () => {
    return [
        <div className="row connection-dash-stats">
          <div className="col-md-6">
            <div className="info-box">
              <span className="info-box-icon bg-orange">
                <img alt="connection" src={ this.renderLogo() } className="center-block ethernet-icon"/>
              </span>
              <div className="info-box-content">
                <h4>CONNECTION SIGNAL</h4>
                <p>{ this.state.system.network.connection.connection_type }</p>
              </div>
            </div>
          </div>


          <div className="col-md-6">
            <div className="info-box">
              { this.renderBatteryInfo(this.state.system.battery.battery_level) }
              <div className="info-box-content">
                <h4>CHARGE LEVEL</h4>
                <p>{ this.state.system.battery.battery_level }%</p>
              </div>
            </div>
          </div>
        </div>,

        <div className="row connection-dash-stats">
          <div className="col-md-6">
              <div className="info-box">
                <span className="info-box-icon bg-aqua">
                  <i className="fa fa-tachometer big-icon"/>
                </span>
                <div className="info-box-content">
                  <h4>CONNECTION SPEED</h4>
                  <ul>
                    <li>
                      <i className="fa fa-chevron-circle-up "></i>
                      <span className="speed">{ this.humanizeSpeed(this.state.system.network.connection.up_speed * 8) }</span> 
                      <br/>
                      <span className="traffic">Upload</span>
                    </li>
                    <li>
                      <i className="fa fa-chevron-circle-down"></i>
                      <span className="speed">{ this.humanizeSpeed(this.state.system.network.connection.down_speed * 8) }</span> 
                      <br/>
                      <span className="traffic">Download</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>


            <div className="col-md-6">
              <div className="info-box">
                <span className="info-box-icon bg-yellow">
                  <i className="fa fa-mobile big-icon"/>
                </span>
                <div className="info-box-content">
                  <h4>DEVICES CONNECTED</h4>
                  <p>{ this.state.system.network.connected_clients }</p>
                </div>
              </div>
            </div>
          </div>,

          <div className="row">
            <div className="col-md-6">
              <div className="box">
                <div className="box-header with-border">
                  <h3 className="box-title">Storage</h3>
                </div>
                <div className="box-body">
                  <p>Your SupaBRCK has <strong>{ Humanize.fileSize(this.state.system.storage.total_space) }</strong> of storage. To access web, go to local.brck (192.168.88.1:8080)</p>
                  <div className="progress">
                    <div className="progress-bar progress-bar-yellow" role="progressbar" aria-valuenow={this.getStorageUsage()} aria-valuemin="0" aria-valuemax="100" style={{width: this.getStorageUsage() + '%'}}>1.5GB used
                      <span className="sr-only">{this.getStorageUsage()}% Complete (warning)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-md-6">
              <div className="box">
                <div className="box-header with-border">
                  <h3 className="box-title">Plex</h3>
                </div>
                <div className="box-body">

                  <p>Your SupaBRCK is enabled with a dual core x86 processor. We have pre-installed plex for you. To find out more go to www...</p>

                  <div className="toggle-component ">
                    <label className="toggle">
                      <input type="checkbox"/>
                      <div data-off="Off" data-on="On"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
    ];
  }

  render() {
    return (
      <Container>
        <div>
          <Header>Dashboard</Header>
          <div className="content container-fluid">
            {(this.state.has_data)
              ? this.renderBody()
              : <Loading />}
          </div>
        </div>
      </Container>
    );
  }
}

export default Dashboard;

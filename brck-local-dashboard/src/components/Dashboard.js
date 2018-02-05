import React, { Component } from 'react';

import Container from './Container';
import Header from './Header';
import Loading from './Loading'
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
      <span class={containerClass}>
        <i class={iconClass} />
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
    } else if (_conn == 'WAN') {
      icon = IconSIM;
    }
    return icon;
  }

  renderBody = () => {
    return(
      <div class="content container-fluid">
        <div class="row connection-dash-stats">
          <div class="col-md-6">
            <div class="info-box">
              <span class="info-box-icon bg-orange">
                <img alt="connection" src={ this.renderLogo() } class="center-block ethernet-icon"/>
              </span>
              <div class="info-box-content">
                <h4>CONNECTION SIGNAL</h4>
                <p>{ this.state.system.network.connection.connection_type }</p>
              </div>
            </div>
          </div>


          <div class="col-md-6">
            <div class="info-box">
              { this.renderBatteryInfo(this.state.system.battery.battery_level) }
              <div class="info-box-content">
                <h4>CHARGE LEVEL</h4>
                <p>{ this.state.system.battery.battery_level }%</p>
              </div>
            </div>
          </div>
        </div>

        <div class="row connection-dash-stats">
          <div class="col-md-6">
              <div class="info-box">
                <span class="info-box-icon bg-aqua">
                  <i class="fa fa-tachometer big-icon"/>
                </span>
                <div class="info-box-content">
                  <h4>CONNECTION SPEED</h4>
                  <ul>
                    <li>
                      <i class="fa fa-chevron-circle-up "></i>
                      <span class="speed">{ this.humanizeSpeed(this.state.system.network.connection.up_speed * 8) }</span> 
                      <br/>
                      <span class="traffic">Upload</span>
                    </li>
                    <li>
                      <i class="fa fa-chevron-circle-down"></i>
                      <span class="speed">{ this.humanizeSpeed(this.state.system.network.connection.down_speed * 8) }</span> 
                      <br/>
                      <span class="traffic">Download</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>


            <div class="col-md-6">
              <div class="info-box">
                <span class="info-box-icon bg-yellow">
                  <i class="fa fa-mobile big-icon"/>
                </span>
                <div class="info-box-content">
                  <h4>DEVICES CONNECTED</h4>
                  <p>{ this.state.system.network.connected_clients }</p>
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6">
              <div class="box">
                <div class="box-header with-border">
                  <h3 class="box-title">Storage</h3>
                </div>
                <div class="box-body">
                  <p>Your SupaBRCK has <strong>{ Humanize.fileSize(this.state.system.storage.total_space) }</strong> of storage. To access web, go to local.brck (192.168.88.1:8080)</p>
                  <div class="progress">
                    <div class="progress-bar progress-bar-yellow" role="progressbar" aria-valuenow={this.getStorageUsage()} aria-valuemin="0" aria-valuemax="100" style={{width: this.getStorageUsage() + '%'}}>1.5GB used
                      <span class="sr-only">{this.getStorageUsage()}% Complete (warning)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="box">
                <div class="box-header with-border">
                  <h3 class="box-title">Plex</h3>
                </div>
                <div class="box-body">

                  <p>Your SupaBRCK is enabled with a dual core x86 processor. We have pre-installed plex for you. To find out more go to www...</p>

                  <div class="toggle-component ">
                    <label class="toggle">
                      <input type="checkbox" onclick="toggle(this,event)" />
                      <div data-off="Off" data-on="On"></div>
                    </label>
                  </div>
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
          <Header>Dashboard</Header>
          {(this.state.has_data)
            ? this.renderBody()
            : null}
        </div>
      </Container>
    );
  }
}

export default Dashboard;

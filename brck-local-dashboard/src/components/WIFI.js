import React, { Component } from 'react';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

import { AlertSuccess,
         AlertWarning,
         AlertError } from './Alerts';

import IconWIFI from '../media/icons/icon_wifi.svg';

const STATE_NONE = "none";

const CHANNEL_OPTIONS = [
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '10',
  '11',
  '12',
  '13',
  '14',
  '15',
  '16',
  '34',
  '36',
  '38',
  '40',
  '42',
  '44',
  '46',
  '48',
  '50',
  '52',
  '54',
  '56',
  '58',
  '60',
  '62',
  '64',
  '100',
  '102',
  '104',
  '106',
  '108',
  '110',
  '112',
  '114',
  '116',
  '118',
  '120',
  '122',
  '124',
  '126',
  '128',
  '132',
  '134',
  '136',
  '138',
  '140',
  '142',
  '144',
  '149',
  '151',
  '153',
  '155',
  '157',
  '159',
  '161',
  '165',
  '169',
  '173',
  '183',
  '184',
  '185',
  '187',
  '188',
  '189',
  '192',
  '196']

const CHECKBOX_CONFIG = {
  hidden: ['1', '0']
}

class WIFI extends Component {

  constructor(props) {
    super(props);
    this.state = {
      current_conn: {},
      loaded: false,
      connections: [],
      mode: '',
      encryption: 'none',
      ssid: '',
      key: '',
      channel: '',
      hidden: '0',
      hwmode: ''
    }
  }

  componentDidMount() {
    this.loadConnections();
    this.interval = window.setInterval(this.loadConnections, 10000);
  }

  componentWillUnmount() {
    if(this.interval) {
      window.clearInterval(this.interval);
    }
  }

  loadConnections = () => {
    if (!this.state.connecting) {
      API.get_wifi_connections(this.dataCallback);
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
      this.setState({
        loaded: true,
        connections: res.body
      });
    }
  }

  
  handleInput = (e) => {
    var newState = {};
    newState[e.target.name] = e.target.value;
    this.setState(newState);
  }

  handleCheckbox = (e) => {
    var newState = {};
    var actual_flag = e.target.checked;
    var conf = CHECKBOX_CONFIG[e.target.name];
    if (conf !== undefined) {
      actual_flag = e.target.checked ? conf[0] : conf[1];
    }
    newState[e.target.name] = actual_flag;
    this.setState(newState);
  }

  handleConfigureWIFI = (conn) => {
    this.setState(conn.info);
    this.setState({
      current_conn: conn
    });
  }

  handleSubmitWIFI = (e) => {
    e.preventDefault();
    var config = {
      mode: this.state.mode,
      encryption: this.state.encryption,
      ssid: this.state.ssid,
      key: this.state.key,
      channel: this.state.channel,
      hidden: this.state.hidden,
      hwmode: this.state.hwmode
    }
    var payload = { configuration: config }
    this.setState({ working: true, connecting: true });
    API.configure_wifi_connection(this.state.current_conn.id, payload, this.configCallback);
  }


  handleViewNetworkInfo = (e, conn) => {
    e.preventDefault();
    this.setState({
      current_conn: conn
    });
  }

  configCallback = (res) => {
    this.setState({ working: false, connecting: false });
    if (!res.ok) {
        this.setState({
            config_error: true
        });
    } else {
        var connections = this.state.connections;
        var new_conn = res.body;
        var v_index = Number.parseInt(new_conn.id.charAt(4), 10);
        connections[v_index-1] = new_conn;
        this.setState({
            config_saved: true,
            connections: connections
        });
        this.loadConnections();
    }
  }

  connCallback = (err, res) => {
    this.setState({ working: false, connecting: false });
    if (err || !res.ok) {
      this.setState({
          conn_error: true
      });
    } else {
      var connections = this.state.connections;
      res.body.map((s) => {
        var v_index = Number.parseInt(s.id.charAt(8), 10);
        connections[v_index-1] = s;
      });

      this.setState({
          conn_error: !res.body[0].connected,
          connections: connections
      });
      this.loadConnections();
    }
  }

  renderNoDevice = (conn) => {
    return(
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: No Cable</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-muted"></i><small>Not Available</small>
            </p>
            <img src={IconWIFI} alt="WiFi" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-default disabled btn-block " data-toggle="modal" >Install Card</a>
          </div>
        </div>
      </div>
    );
  }

  renderConfigureWIFI = (conn) => {
    return (
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: Available</h3>
          </div>
          <div className="box-body">
            { (conn.info.mode === 'ap')
              ? <p className="text-center"><i className="fa fa-wifi text-red "></i><small>Broadcasting</small></p>
              : <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small></p>
            }
            <img src={IconWIFI} alt="WiFi" className="center-block connectivity-icon" />
            <a href="#" onClick={(e) => this.handleConfigureWIFI(conn) } className="btn btn-primary btn-block" data-toggle="modal" data-target="#wifi2">Configure</a>
          </div>
        </div>
      </div>
    );
  }


  renderConnecting= (conn) => {
    return (
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconWIFI} alt="WiFi" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-primary disabled btn-block"><span className="pull-right"><i className="fa fa-spin fa-refresh"></i></span> Connecting </a>
          </div>
        </div>
      </div>
    );
  }

  renderActiveWIFI = (conn) => {
    return (
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: Active </h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-check-circle text-green "></i><small>Connected</small>
            </p>
            <img src={IconWIFI} alt="WiFi" className="center-block connectivity-icon" />
            <a href="#" onClick={(e) => this.handleViewNetworkInfo(e, conn)} className="btn btn-success btn-block" data-toggle="modal" data-target="#wifi-signal-info">View</a>
          </div>
        </div>
      </div>
    );
  }

  renderConn = (conn) => {
    var isConnecting = (conn.id === this.state.current_conn.id) && (this.state.connecting);
    if(conn.connected) {
      return this.renderActiveWIFI(conn);
    } else if (conn.available && !conn.connected && isConnecting) {
      return this.renderConnecting(conn);
    } else if (conn.available && !conn.connected) {
      return this.renderConfigureWIFI(conn);
    } else {
      return this.renderNoDevice(conn);
    }
  }

  renderConfigureWIFIDialog = () => {
    return (
      <div className="modal fade" id="wifi2" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span> </button>
              <h4 className="modal-title" id="myModalLabel">WiFi Settings</h4>
            </div>

            <div className="modal-body">
              <div className="row"> 
                  <form>
                    <div className="col-md-12">
                      <div className="form-group">
                        <label>Operation Mode</label>
                        <select
                          name="mode"
                          className="form-control fancy-select"
                          value={ this.state.mode }
                          onChange={ this.handleInput }>
                            <option value="ap">Access Point</option>
                            <option value="sta">Client</option>
                          </select>
                      </div>
                      <div className="form-group">
                        <label>SSID</label>
                        <input name="ssid" className="form-control" type="text" value={ this.state.ssid } onChange={ this.handleInput } />
                      </div>

                      <div className="form-group">
                        <label>Encryption</label>
                        <select
                          name="encryption"
                          className="form-control fancy-select"
                          value={ this.state.encryption }
                          onChange={ this.handleInput }>
                            <option value="none">None</option>
                            <option value="psk">WPA-PSK</option>
                            <option value="psk2">WPA2-PSK</option>
                            <option value="wep">WEP</option>
                            <option value="wpa">WPA</option>
                          </select>
                      </div>

                      <div className="checkbox">
                        <label>
                          <input name="hidden" checked={ (this.state.hidden === '1') } onChange={ this.handleCheckbox } type="checkbox" />
                          Hidden
                        </label>
                      </div>

                      <div className="form-group">
                        <label>Wireless Key</label>
                        <input name="key" disabled={ this.state.encryption === STATE_NONE } className="form-control" type="text" value={ this.state.key } onChange={ this.handleInput } />
                      </div>

                      <div className="form-group">
                        <label>Channel</label>
                        <select
                          name="channel"
                          className="form-control fancy-select"
                          value={ this.state.channel }
                          onChange={ this.handleInput }>
                          {
                            CHANNEL_OPTIONS.map(function(channel, index) {
                              return <option key={ "channel-opt-" + index } value={ channel }>{ channel }</option>
                            })
                          }
                          </select>
                      </div>

                      <div className="form-group">
                        <label>Protocol</label>
                        <select
                          name="hwmode"
                          className="form-control fancy-select"
                          value={ this.state.hwmode }
                          onChange={ this.handleInput }>
                            <option value="11a">11a</option>
                            <option value="11a">11b</option>
                            <option value="11a">11g</option>
                          </select>
                      </div>

                    </div>
                    <div className="col-md-12">                     
                      <a href="#" onClick={ this.handleSubmitWIFI } className="btn btn-primary pull-right" data-dismiss="modal">Save</a>                   
                    </div>
                </form>
              </div>
            </div>
          </div>
        </div>
    </div>
    );
  }



  renderSignalStatusDialog = () => {
    var net_info = {};
    if (this.state.current_conn.id) {
      net_info = this.state.current_conn.info || {};
    }
    return (
      <div className="modal fade" id="wifi-signal-info" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel3">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span> </button>
              <h4 className="modal-title" id="myModalLabel3">Network Information</h4>
            </div>

            <div className="modal-body">
              <table className="table table-bordered table-striped">
                <tbody>
                  <tr>
                    <td>Signal Strength</td>
                    <td>
                      <div className="progress progress-xs">
                        <div className="progress-bar progress-bar-yellow" style={{ width: '100%' }}></div>
                      </div>
                    </td>
                    <td>
                      <span className="badge bg-yellow">100 %</span>
                    </td>
                  </tr>
                  <tr>
                    <td>SSID</td>
                    <td>{ net_info.ssid } { net_info.hidden === '1' ? <span className="label bg-gray">hidden</span> : null }</td>
                  </tr>
                  <tr>
                    <td>Operation Mode</td>
                    <td>{ net_info.mode }</td>
                  </tr>
                  <tr>
                    <td>Protocol</td>
                    <td>{ net_info.hwmode }</td>
                  </tr>
                  <tr>
                    <td>Encryption</td>
                    <td>{ net_info.encryption }</td>
                  </tr>
                  <tr>
                    <td>Channel</td>
                    <td>{ net_info.channel }</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="modal-footer">
              <div className="row">
                <div className="col-md-12">
                  <a href="#" className="btn btn-default pull-right" data-dismiss="modal">Back</a>
                </div>
              </div>
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
            ? <AlertSuccess message={"Your WiFi settings have been successfully applied."} />
            : null)}
          {(this.state.config_error
            ? <AlertError title={"We could not connect with the WiFi information provided"}
                errors={["Make sure the IP configuration is accurate", "Contact your service provider for IP support"]} />
            : null)}
          {(this.state.conn_error
           ? <AlertWarning message={"Could not connect using WiFi."} />
           : null )}
        </div>
      </div>
    )
  }

  render() {
    var that = this;
    return (
      <Container>
        <div>
          <Header>WiFi Connectivity</Header>
          {(this.state.loaded)
          ? null
          : <Loading message="Loading WiFi connections" />}
          <div className="content container-fluid">
            { this.renderMessages() }
            <div className="row">
              {this.state.connections.map(function(conn, index){
                return that.renderConn(conn);
              })}
            </div>
          </div>
        </div>
        { this.renderConfigureWIFIDialog() }
        { this.renderSignalStatusDialog() }
      </Container>
    );
  }
}

export default WIFI;
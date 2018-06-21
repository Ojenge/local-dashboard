import React, { Component } from 'react';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

import { AlertSuccess,
         AlertWarning,
         AlertError } from './Alerts';

import IconLAN from '../media/icons/icon_ethernet.svg';

const STATE_UNKNOWN = 'UNKNOWN';
const STATE_AUTO = "AUTO";

class Ethernet extends Component {

  constructor(props) {
    super(props);
    this.state = {
      current_conn: {},
      loaded: false,
      connections: [],
      dhcp_enabled: true,
      ipaddr: '',
      netmask: '',
      gateway: '',
      dns: ''
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
      API.get_lan_connections(this.dataCallback);
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
    newState[e.target.name] = e.target.checked;
    this.setState(newState);
  }

  handleConfigureLAN = (conn) => {
    this.setState(conn.info.network);
    this.setState({
      dhcp_enabled: conn.info.dhcp_enabled,
      current_conn: conn
    });
  }

  handleSubmitLAN = (e) => {
    e.preventDefault();
    var config = {
      dhcp_enabled: this.state.dhcp_enabled,
      network: {
        ipaddr: this.state.ipaddr,
        netmask: this.state.netmask,
        gateway: this.state.gateway,
        dns: this.state.dns
      }
    }
    var payload = { configuration: config }
    this.setState({ working: true, connecting: true });
    API.configure_lan_connection(this.state.current_conn.id, payload, this.configCallback);
  }


  handleConnect = (e, conn) => {
    e.preventDefault();
    this.setState({
      current_conn: conn
    });
    var payload = { configuration: this.state.current_conn };
    this.setState({ working: true, connecting: true });
    API.configure_lan_connection(conn.id, payload, this.connCallback);
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
        var v_index = Number.parseInt(new_conn.id.charAt(8), 10);
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

  renderNoCable = (conn) => {
    return(
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: No Cable</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-muted"></i><small>Not Inserted</small>
            </p>
            <img src={IconLAN} alt="ETHERNET" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-default disabled btn-block " data-toggle="modal" >Insert Cable</a>
          </div>
        </div>
      </div>
    );
  }

  renderConfigureLAN = (conn) => {
    return (
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconLAN} alt="ETHERNET" className="center-block connectivity-icon" />
            <a href="#" onClick={(e) => this.handleConfigureLAN(conn) } className="btn btn-primary btn-block" data-toggle="modal" data-target="#eth2">Configure</a>
          </div>
        </div>
      </div>
    );
  }

  renderConnect = (conn) => {
    return (
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconLAN} alt="ETHERNET" className="center-block connectivity-icon" />
              <a href="#" onClick={ (e) => this.handleConnect(e, conn) } className="btn btn-primary btn-block" data-toggle="modal" data-target="#eth2-connect">Connect</a>
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
            <img src={IconLAN} alt="ETHERNET" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-primary disabled btn-block"><span className="pull-right"><i className="fa fa-spin fa-refresh"></i></span> Connecting </a>
          </div>
        </div>
      </div>
    );
  }

  renderActiveLAN = (conn) => {
    return (
      <div className="col-md-4 col-sm-6" key={ conn.id }>
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ conn.name }: Active </h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-check-circle text-green "></i><small>Connected</small>
            </p>
            <img src={IconLAN} alt="ETHERNET" className="center-block connectivity-icon" />
            <a href="#" onClick={(e) => this.handleViewNetworkInfo(e, conn)} className="btn btn-success btn-block" data-toggle="modal" data-target="#eth-signal-info">View</a>
          </div>
        </div>
      </div>
    );
  }

  renderConn = (conn) => {
    var isConnecting = (conn.id === this.state.current_conn.id) && (this.state.connecting);
    if(conn.connected) {
      return this.renderActiveLAN(conn);
    } else if (conn.available && !conn.connected && isConnecting) {
      return this.renderConnecting(conn);
    } else if (conn.available && !conn.connected) {
      return this.renderConfigureLAN(conn);
    } else {
      return this.renderNoCable(conn);
    }
  }

  renderConfigureLANDialog = () => {
    return (
      <div className="modal fade" id="eth2" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span> </button>
              <h4 className="modal-title" id="myModalLabel">LAN Settings</h4>
            </div>

            <div className="modal-body">
              <div className="row"> 
                  <form>
                    <div className="col-md-12">
                      <div className="checkbox">
                        <label>
                          <input name="dhcp_enabled" checked={ this.state.dhcp_enabled } onChange={ this.handleCheckbox } type="checkbox" />
                          DHCP
                        </label>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="form-group">
                        <label>Static IP</label>
                        <input name="ipaddr" disabled={ this.state.dhcp_enabled } className="form-control" value={ this.state.ipaddr } onChange={ this.handleInput } type="text" placeholder=" e.g 192.186.0.1" />
                      </div>
                      <div className="form-group">
                        <label>Router</label>
                        <input name="gateway" disabled={ this.state.dhcp_enabled } className="form-control" type="text" value={ this.state.gateway } onChange={ this.handleInput } />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="form-group">
                        <label>Subnet Mask</label>
                        <input name="netmask" disabled={ this.state.dhcp_enabled } className="form-control" type="text" placeholder=" e.g 255.255.255.0" value={ this.state.netmask } onChange={ this.handleInput } />
                      </div>
                      <div className="form-group">
                        <label>DNS Server(s)</label>
                        <input name="dns" disabled={ this.state.dhcp_enabled } className="form-control" type="text" placeholder=" e.g 8.8.8.8" value={ this.state.dns } onChange={ this.handleInput } />
                      </div> 
                      
                      <a href="#" onClick={ this.handleSubmitLAN } className="btn btn-primary pull-right" data-dismiss="modal">Save</a>                   
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
    var net_info = { network: {}};
    if (this.state.current_conn.id) {
      net_info = this.state.current_conn.info || {};
    }
    var dhcp = net_info.dhcp_enabled;
    return (
      <div className="modal fade" id="eth-signal-info" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel3">
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
                    <td>Protocol</td>
                    <td>{ dhcp ? <span>DHCP</span> : <span>Static</span> }</td>
                  </tr>
                  <tr>
                    <td>IP Address</td>
                    <td>{ net_info.network.ipaddr || STATE_UNKNOWN }</td>
                  </tr>
                  <tr>
                    <td>Netmask</td>
                    <td>{ net_info.network.netmask || (dhcp ? STATE_AUTO : STATE_UNKNOWN) }</td>
                  </tr>
                  <tr>
                    <td>Gateway</td>
                    <td>{ net_info.network.gateway || (dhcp ? STATE_AUTO : STATE_UNKNOWN) }</td>
                  </tr>
                  <tr>
                    <td>DNS</td>
                    <td>{ net_info.network.dns || (dhcp ? STATE_AUTO : STATE_UNKNOWN) }</td>
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
            ? <AlertSuccess message={"Your Ethernet settings have been successfully applied."} />
            : null)}
          {(this.state.config_error
            ? <AlertError title={"We could not connect with the ethernet information provided"}
                errors={["Make sure the IP configuration is accurate", "Contact your service provider for IP support"]} />
            : null)}
          {(this.state.conn_error
           ? <AlertWarning message={"Could not connect using Ethernet."} />
           : null )}
        </div>
      </div>
    )
  }

  render() {
    var that = this;
    return (
      <div>
        <div>
          <Header>Ethernet Connectivity</Header>
          {(this.state.loaded)
          ? null
          : <Loading message="Loading Ethernet connections" />}
          <div className="content container-fluid">
            { this.renderMessages() }
            <div className="row">
              {this.state.connections.map(function(conn, index){
                return that.renderConn(conn);
              })}
            </div>
          </div>
        </div>
        { this.renderConfigureLANDialog() }
        { this.renderSignalStatusDialog() }
      </div>
    );
  }
}

export default Ethernet;

import React, { Component } from 'react';
import io from 'socket.io-client';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

import { AlertSuccess,
         AlertWarning,
         AlertError } from './Alerts';

import IconSim from '../media/icons/icon-sim.svg';

const CONNECTING_TIMEOUT = 10000;

const ENABLE_3G_MONITOR = 'ENABLE_3G_MONITOR';
const REQUIRES_PIN = 'REQUIRES_PIN';
const REQUIRES_PUK = 'REQUIRES_PUK';
const REQUIRES_APN = 'REQUIRES_APN';

const FAILURE_STATES = [
  'NO_CONNECTION',
  'PIN_REJECTED',
  'NO_CARRIER',
  'NO_CONNECTION'
];

class SIMConnections extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      connected: true,
      connections: [],
      conn_events: [],
      last_event: null,
      apn: '',
      apn_user: '',
      apn_password: '',
      pin: '',
      puk: '',
      errors: {}
    }
  }

  componentDidMount() {
    this.loadConnections();
    this.interval = window.setInterval(this.loadConnections, 10000);
    this.initializeSocket();
  }

  componentWillUnmount() {
    if(this.interval) {
      window.clearInterval(this.interval);
    }
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
    this.socket = io('/sim-connectivity', opts);
    this.socket.on('conn_event', (data) => {
      var _conn_events = this.state.conn_events;
      _conn_events.push(data);
      this.setState({
        conn_events: _conn_events,
        last_event: data.event
      });
      if (FAILURE_STATES.indexOf(data.event) >= 0) {
        this.setState({
          conn_error: true
        });
      }
    }); 
  }

  loadConnections = () => {
    if (!this.state.connecting) {
      API.get_sim_connections(this.dataCallback);
    }
  }

  clearConnecting = () => {
    this.setState({ connecting: false });
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
  
  handleConfigureAPN = (sim) => {
    this.setState({
      sim_id: sim.id,
      current_sim: sim
    });
  }


  resetConnState = () => {
    this.setState({
      last_event: null,
      conn_error: false,
      config_error: false,
      conn_events: []
    });
  }

  handleSubmitAPN = (e) => {
    e.preventDefault();
    this.resetConnState();
    var config = {
      network: {
        apn: this.state.apn,
        username: this.state.apn_user,
        password: this.state.apn_password
      }
    }
    var payload = { configuration: config }
    this.setState({ working: true, connecting: true });
    API.configure_sim_connection(this.state.sim_id, payload, this.configCallback);
  }


  handleSubmitPIN = (e) => {
    e.preventDefault();
    this.resetConnState();
    var config = {};
    if (this.state.pin) {
      config.pin = this.state.pin
    }
    if (this.state.puk) {
      config.puk = this.state.puk;
    }
    var payload = { configuration: config }
    this.setState({ working: true, connecting: true });
    API.configure_sim_connection(this.state.sim_id, payload, this.configCallback);
  }


  handleConnect = (e, sim) => {
    e.preventDefault();
    this.setState({
      sim_id: sim.id,
      current_sim: sim,
      conn_error: false
    });
    var payload = { configuration: {} };
    this.setState({ working: true, connecting: true });
    API.configure_sim_connection(sim.id, payload, this.connCallback);
  }

  handleConnectSIM = (e, sim) => {
    e.preventDefault();
    this.resetConnState();
    this.setState({
      sim_id: sim.id,
      current_sim: sim,
    });
    var payload = { configuration: {} };
    this.setState({ working: true, connecting: true });
    API.configure_sim_connection(sim.id, payload, this.connCallback);
  }

  handleCloseConnecting = (e) => {
    e.preventDefault();
    this.setState({
      conn_events: [],
      last_event: null
    })
  }

  handleUnlockSIM = (e, sim) => {
    e.preventDefault();
    this.setState({
      sim_id: sim.id,
      current_sim: sim
    });
  }

  handleViewNetworkInfo = (e, sim) => {
    e.preventDefault();
    this.setState({
      sim_id: sim.id,
      current_sim: sim
    });
  }

  configCallback = (res) => {
    this.setState({ working: false, connecting: false });
    if (!res.ok) {
        this.setState({
            config_error: true,
            errors: res.body.errors || {}
        });
    } else {
        var connections = this.state.connections;
        res.body.map((s) => {
          var v_index = Number.parseInt(s.id.charAt(3), 10);
          connections[v_index-1] = s;
        });

        this.setState({
            config_saved: true,
            connections: connections
        });
        this.loadConnections();
    }
  }

  connCallback = (res) => {
    this.setState({ working:false, connecting: false });
    if (!res.ok) {
      this.setState({
          conn_error: true
      });
    } else {
      var connections = this.state.connections;
      res.body.map((s) => {
        var v_index = Number.parseInt(s.id.charAt(3), 10);
        connections[v_index-1] = s;
      });

      this.setState({
          connections: connections
      });
      this.loadConnections();
    }
  }

  renderNoSim = (sim) => {
    return(
      <div className="col-md-4 col-sm-6" key={ sim.id }>
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: No SIM</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-muted"></i><small>Not Inserted</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-default disabled btn-block " data-toggle="modal" >Insert Sim</a>
          </div>
        </div>
      </div>
    );
  }

  renderConfigureSim = (sim) => {
    return (
      <div className="col-md-4 col-sm-6" key={ sim.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            { (sim.info.pin_locked || sim.info.puk_locked)
              ? (
                <a href="#" onClick={(e) => { e.preventDefault(); this.handleUnlockSIM(e, sim) }} value={sim.id} className="btn btn-danger btn-block" data-toggle="modal" data-target="#sim-locked">Set PIN</a>
              ): (
                <a href="#" onClick={(e) => this.handleConfigureAPN(sim) } value={sim.id} className="btn btn-primary btn-block" data-toggle="modal" data-target="#sim2">Configure APN</a>
              ) }
          </div>
        </div>
      </div>
    );
  }

  renderConnect = (sim) => {
    return (
      <div className="col-md-4 col-sm-6" key={ sim.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            { (sim.info.pin_locked || sim.info.puk_locked)
              ? (
                <a href="#" onClick={ (e) => { e.preventDefault(); this.handleUnlockSIM(e, sim) }} className="btn btn-danger btn-block" data-toggle="modal" data-target="#sim-locked">Set PIN</a>
              ) : (
                <a href="#" onClick={ (e) => this.handleConnect(e, sim) } className="btn btn-primary btn-block" data-toggle="modal" data-target="#sim2-connect">Connect</a>
              )
            }
          </div>
        </div>
      </div>

    );
  }

  renderConnectSIM = (sim) => {
    return (
      <div className="col-md-4 col-sm-6" key={ sim.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" onClick={ (e) => this.handleConnectSIM(e, sim) } className="btn btn-primary btn-block" data-backdrop='static' data-keyboard="false" data-toggle="modal" data-target="#sim-connect">Connect</a>
          </div>
        </div>
      </div>
    );
  }

  renderConnecting= (sim) => {
    return (
      <div className="col-md-4 col-sm-6" key={ sim.id }>
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-primary disabled btn-block"><span className="pull-right"><i className="fa fa-spin fa-refresh"></i></span> Connecting </a>
          </div>
        </div>
      </div>
    );
  }

  renderActiveSIM = (sim) => {
    return (
      <div className="col-md-4 col-sm-6" key={ sim.id }>
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Active </h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-check-circle text-green "></i><small>Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" onClick={(e) => this.handleViewNetworkInfo(e, sim)} value={sim.id} className="btn btn-success btn-block" data-toggle="modal" data-target="#sim-signal-info">View</a>
          </div>
        </div>
      </div>
    );
  }

  renderSim = (sim) => {
    var isConnecting = (sim.id === this.state.sim_id) && (this.state.connecting);
    if(sim.connected) {
      return this.renderActiveSIM(sim);
    } else if (sim.available) {
      return this.renderConnectSIM(sim);
    // } else if (sim.available && !sim.connected && sim.info.apn_configured && (sim.info.pin_locked || sim.info.puk_locked)) {
    //   return this.renderConfigureSim(sim);
    // } else if (sim.available && !sim.connected && sim.info.apn_configured) {
    //   return this.renderConnect(sim);
    // } else if (sim.available && !sim.connected && !sim.info.pin_locked) {
    //   return this.renderConfigureSim(sim);
    } else {
      return this.renderNoSim(sim);
    }
  }

  renderConfigureSimDialog = () => {
    return (
      <div className="modal fade" id="sim2" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span> </button>
              <h4 className="modal-title" id="myModalLabel">APN Settings</h4>
            </div>

            <div className="modal-body">
              <div className="row">
                <div className="col-md-6">
                  <div className="alert alert-danger">
                    We can't connect to the internet with your SIM card. Please ensure the SIM is Data Enabled, has credit and has valid APN
                  </div>

                  <p>The 3G/4G modem supports all GSM and HSPA+ providers, but unfortunately not CDMA (Verison and Sprint in the U.S).</p>
                  <p>In case you don't know your APN settings, please contact your service provider.</p>

                </div>
                
                <div className="col-md-6 mobile-top-spacing-15">
                  <form>
                    <div className="form-group">
                      <label>APN</label>
                      <input className="form-control" type="text" name="apn" value={ this.state.apn } 
                        onChange={ this.handleInput } />
                    </div>
                    <div className="form-group">
                      <label>Username</label>
                      <input className="form-control" type="text" name="apn_user" value={ this.state.apn_user }
                        onChange={ this.handleInput } />
                    </div>
                    <div className="form-group">
                      <label>Password</label>
                      <input className="form-control" type="password" name="apn_password" value={ this.state.apn_password }
                        onChange={ this.handleInput } />
                    </div>

                    <a href="." onClick={ this.handleSubmitAPN } className="btn btn-primary pull-right" data-dismiss="modal">Save</a>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
    );
  }

  renderConnectSimDialog = () => {
    const eventSize = this.state.conn_events.length;
    const last_event = eventSize - 1;
    const done = this.state.last_event == ENABLE_3G_MONITOR;
    const iconClass = "fa fa-check text-white";
    const iconClassActive = "fa fa-spinner fa-spin text-yellow";
    const lastFive = (last_event - 5);
    const minIndex = (lastFive >= 0) ? lastFive : 0;
    return (
      <div className="modal fade" id="sim-connect" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h4 className="modal-title" id="myModalLabel">Connecting</h4>
            </div>

            <div className="modal-body">
              <div className="row">
                <div className="col-md-12">
                  { this.state.conn_events.map(function(conn_event, index) {
                      if (index === last_event) {
                        return (
                          <div className="alert bg-gray" key={ "conn-event-" + index }>
                            <h4>
                              <i className={ done ? iconClass : iconClassActive } /> { conn_event.description }
                            </h4>
                          </div>
                        )
                      } else if (index >= minIndex) {
                        return (
                          <div className="alert bg-gray" key={ "conn-event-" + index }>
                            <p>
                              <i className={ iconClass } /> { conn_event.description }
                            </p>
                          </div>
                        )
                      }
                  }) }
                  { (this.state.last_event == REQUIRES_PIN)
                    ? (
                        <div className="input-group">
                            <span className="input-group-addon">PIN</span>
                            <input type="number" name="pin" value={ this.state.pin } onChange={ this.handleInput } className="form-control" />
                            <span className="input-group-btn">
                                <button className="btn btn-primary btn-flat" onClick={ this.handleSubmitPIN }>Save</button>
                            </span>
                        </div>
                    ) : null

                  }
                  { (this.state.last_event == REQUIRES_PUK)
                    ? (
                      <div>
                        <div className="input-group">
                            <span className="input-group-addon">PUK</span>
                            <input type="number" name="puk" value={ this.state.puk } onChange={ this.handleInput } className="form-control" />
                        </div>
                        <div className="input-group">
                            <span className="input-group-addon">NEW PIN</span>
                            <input type="number" name="pin" value={ this.state.pin } onChange={ this.handleInput } className="form-control" />
                        </div>
                        <div className="input-group">
                          <button className="btn btn-primary btn-flat" onClick={ this.handleSubmitPIN }>Save</button>
                        </div>
                      </div>
                    ) : null

                  }
                  { (this.state.last_event == REQUIRES_APN)
                    ? (
                        <div className="input-group">
                            <span className="input-group-addon">APN</span>
                            <input type="text" name="apn" value={ this.state.apn } onChange={ this.handleInput } className="form-control" />
                            <span className="input-group-btn">
                                <button className="btn btn-primary btn-flat" onClick={ this.handleSubmitAPN }>Save</button>
                            </span>
                        </div>
                    ) : null

                  }
                </div>
              </div>
            </div>
            <div className="modal-footer">
              { (this.state.last_event == ENABLE_3G_MONITOR)
                ? <a href="." onClick={ this.handleCloseConnecting } className="btn btn-primary btn-block" data-toggle="modal" data-target="#sim-connect">Done</a>
                : null
              }
            </div>
          </div>
        </div>
    </div>
    );
  }

  renderConfigureSimLockedDialog = () => {
    const pukLocked = this.state.current_sim ? this.state.current_sim.info.puk_locked : false;
    return (
      <div className="modal fade" id="sim-locked" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span> </button>
              <h4 className="modal-title" id="myModalLabel">SIM Locked</h4>
            </div>

            <div className="modal-body">
              <div className="row">
                <div className="col-md-12">
                  <p>
                    { pukLocked
                      ? (
                        <span>This SIM requires a PUK and PIN to connect.</span>
                      ): (
                        <span>This SIM requires a PIN to connect.</span>
                      ) }
                  </p>
                </div>
                <div className="col-md-12 mobile-top-spacing-15">
                  <form>
                    { pukLocked
                    ? (
                      <div className="form-group">
                        <label>PUK</label>
                        <input className="form-control" type="number" name="puk" value={ this.state.puk } 
                          onChange={ this.handleInput } />
                      </div>
                    ) : (
                      null
                    )}
                    <div className="form-group">
                      <label>PIN</label>
                      <input className="form-control" type="text" name="pin" value={ this.state.pin }
                        onChange={ this.handleInput } />
                    </div>
                    <a href="." onClick={ this.handleSubmitPIN } className="btn btn-primary pull-right" data-dismiss="modal">Save</a>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
     </div>
    );
  }


  renderSignalStatusDialog = () => {
    var net_info = {};
    if (this.state.current_sim) {
      net_info = this.state.current_sim.info.network_info || {};
    }
    return (
      <div className="modal fade" id="sim-signal-info" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel3">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span> </button>
              <h4 className="modal-title" id="myModalLabel3">Network Signal Information</h4>
            </div>

            <div className="modal-body">
              <table className="table table-bordered table-striped">
                <tbody>
                  <tr>
                    <td>Signal Strength</td>
                    <td>
                      <div className="progress progress-xs">
                        <div className="progress-bar progress-bar-yellow" style={{ width:  net_info.signal_strength + '%' }}></div>
                      </div>
                    </td>
                    <td>
                      <span className="badge bg-yellow">{ net_info.signal_strength }%</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Operator</td>
                    <td>{ net_info.operator }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>Network Type</td>
                    <td>{ net_info.net_type }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>IMEI</td>
                    <td>{ net_info.imei }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>IMSI</td>
                    <td>{ net_info.imsi }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>MCC</td>
                    <td>{ net_info.mcc }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>MNC</td>
                    <td>{ net_info.mnc }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>Cell ID</td>
                    <td>{ net_info.cell_id }</td>
                    <td/>
                  </tr>
                  <tr>
                    <td>Location Code</td>
                    <td>{ net_info.lac }</td>
                    <td/>
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
    const default_errors = ["Make sure the SIM is data-enabled and has data bundles or credit",
                            "Make sure the APN/PIN/PUK information is typed in correctly",
                            "Make sure the PIN is correct or disabled"];
    var errors = [];
    if (this.state.errors) {
      for (var key in this.state.errors) {
        errors.push(this.state.errors[key]);
      }
    }
    errors = errors.concat(default_errors);
    return (
      <div className="row">
        <div className="col-xs-12">
          {(this.state.config_saved
            ? <AlertSuccess message={"Your APN settings have been successfully configured."} />
            : null)}
          {((this.state.config_error && !this.state.connecting)
            ? <AlertError title={"We could not connect with the APN/PIN information provided"}
                errors={ errors } />
            : null)}
          {((this.state.conn_error && !this.state.connecting)
           ? <AlertError title={"Could not connect with the selected SIM - You can try another SIM."} errors={errors} />
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
          <Header>SIM Connectivity</Header>
          {(this.state.loaded)
          ? null
          : <Loading message="Loading SIM connections" />}
          <div className="content container-fluid">
            { this.renderMessages() }
            <div className="row">
              {this.state.connections.map(function(sim, index){
                return that.renderSim(sim);
              })}
            </div>
          </div>
        </div>
        { this.renderConnectSimDialog() }
        { this.renderConfigureSimDialog() }
        { this.renderConfigureSimLockedDialog() }
        { this.renderSignalStatusDialog() }
      </Container>
    );
  }
}

export default SIMConnections;
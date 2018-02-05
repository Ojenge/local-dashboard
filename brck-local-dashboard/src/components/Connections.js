import React, { Component } from 'react';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

import IconSim from '../media/icons/icon-sim.svg';

const Loader = props =>
  <div className="alert">
    <div class="center-text spinner" />
  </div>

const AlertSuccess = props => {
  return (
    <div class="alert alert-success alert-dismissible">
      <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
      { props.message }
    </div>
  );
}

const AlertError = props => {
  return (
    <div class="alert alert-danger alert-dismissible">
      <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
      <h4>{ props.title }</h4>
      <ol>
        {props.errors.map((err, key) => 
          <li key={key}>{ err }</li>
         )}
      </ol>
  </div>
  );
}

class Connections extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      connections: [],
      apn: '',
      apn_user: '',
      apn_password: ''
    }
  }

  componentDidMount() {
    API.get_sim_connections(this.dataCallback);
  }

  dataCallback = (err, res) => {
    if (err || !res.ok) {
      this.setState({
        loaded: false,
        net_error: true
      });
      API.handle_error(res.status);
    } else {
      this.setState({
        loaded: true,
        connections: res.body
      });
    }
  }

  handleConfigureAPN = (sim) => {
    this.setState({
      sim_id: sim.id
    });
  }

  handleInput = (e) => {
    var newState = {};
    newState[e.target.name] = e.target.value,
    this.setState(newState);
  }

  handleSubmitAPN = (e) => {
    e.preventDefault();
    var config = {
      network: {
        apn: this.state.apn,
        username: this.state.apn_user,
        password: this.state.apn_password
      }
    }
    var payload = { configuration: config }
    this.setState({ working: true });
    API.configure_sim_connection(this.state.sim_id, payload, this.connCallback);
  }

  connCallback = (err, res) => {
    this.setState({ working: false });
    if (err || !res.ok) {
        this.setState({
            config_error: true
        });
    } else {
        this.setState({
            config_saved: true
        });
    }
  }

  renderNoSim = (sim) => {
    return(
      <div className="col-md-4 col-sm-6" key={sim.id}>
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
      <div className="col-md-4 col-sm-6">
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" onClick={(e) => this.handleConfigureAPN(sim)} value={sim.id} className="btn btn-primary btn-block" data-toggle="modal" data-target="#sim2">Configure</a>
          </div>
        </div>
      </div>
    );
  }

  renderConfigurePIN = (sim) => {
    return (
      <div className="col-md-4 col-sm-6 ">
        <div className="box box-solid connection-type">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Available</h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-times-circle text-red "></i><small>Not Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-primary btn-block" data-toggle="modal" data-target="#sim2-connect">Connect</a>
          </div>
        </div>
      </div>

    );
  }

  renderConnectingPIN = (sim) => {
    return (
      <div className="col-md-4 col-sm-6 ">
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
      <div className="col-md-4 col-sm-6">
        <div className="box box-solid connection-type disabled">
          <div className="box-header with-border">
            <h3 className="box-title text-center">{ sim.name }: Active </h3>
          </div>
          <div className="box-body">
            <p className="text-center"><i className="fa fa-check-circle text-green "></i><small>Connected</small>
            </p>
            <img src={IconSim} alt="SIM" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-success btn-block " data-toggle="modal" data-target="#sim3">View</a>
          </div>
        </div>
      </div>
    );
  }

  renderSim = (sim) => {
    if(sim.connected) {
      return this.renderActiveSIM(sim);
    } else if (sim.available && !sim.connected && !sim.info.pin_locked) {
      return this.renderConfigureSim(sim);
    } else if (sim.available && !sim.connected && sim.info.pin_locked) {
      return this.renderConfigurePIN(sim);
    } else if (sim.available && !sim.connected && sim.info.apn_configured && sim.connecting) {
      return this.renderConnectingPIN(sim);
    } else {
      return this.renderNoSim(sim);
    }
  }

  renderConfigureSimDialog = () => {
    return (
      <div className="modal fade" id="sim2" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
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

  renderMessages = () => {
    return (
      <div class="row">
        <div class="col-xs-12">
          {this.state.working ? <Loader /> : null }
          {(this.state.config_saved
            ? <AlertSuccess message={"Your APN settings have been successfully configured."} />
            : null)}
          {(this.state.config_error
            ? <AlertError title={"We could not connect with the APN information provided"}
                errors={["Make sure the APN information is typed in correctly", "Contact your mobile service provider for APN support"]} />
            : null)}
        </div>
      </div>
    )
  }

  render() {
    var that = this;
    return (
      <Container>
        <div>
          <Header>Connectivity (SIM Assets)</Header>
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
        { this.renderConfigureSimDialog() }
      </Container>
    );
  }
}

export default Connections;
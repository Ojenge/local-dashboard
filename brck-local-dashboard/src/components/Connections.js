import React, { Component } from 'react';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

class Connections extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      connections: []
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
            <img src="/dist/img/icons/icon-sim.svg" className="center-block connectivity-icon" />
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
            <img src="/dist/img/icons/icon-sim.svg" className="center-block connectivity-icon"/>
            <a href="#" className="btn btn-primary btn-block" data-toggle="modal" data-target="#sim2">Configure</a>
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
            <img src="/dist/img/icons/icon-sim.svg" className="center-block connectivity-icon"/>
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
            <img src="/dist/img/icons/icon-sim.svg" className="center-block connectivity-icon" />
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
            <img src="/dist/img/icons/icon-sim.svg" className="center-block connectivity-icon" />
            <a href="#" className="btn btn-success btn-block " data-toggle="modal" data-target="#sim3">View</a>
          </div>
        </div>
      </div>
    );
  }

  renderSim = (sim) => {
    if(sim.connected) {
      return this.renderActiveSIM(sim);
    } else if (sim.available && !sim.connected && !sim.info.apn_configured) {
      return this.renderConfigureSim(sim);
    } else if (sim.available && !sim.connected && sim.info.pin_locked) {
      return this.renderConfigurePIN(sim);
    } else if (sim.available && !sim.connected && sim.info.apn_configured && !sim.info.pin_locked) {
      return this.renderConnectingPIN(sim);
    } else {
      return this.renderNoSim(sim);
    }
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
            <div className="row">
              {this.state.connections.map(function(sim, index){
                return that.renderSim(sim);
              })}
            </div>
          </div>
        </div>
      </Container>
    );
  }
}

export default Connections;
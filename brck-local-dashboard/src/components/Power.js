import React, { Component } from 'react';

import {AlertError,
        AlertInfo,
        AlertSuccess} from './Alerts';

import API from '../utils/API';
import Container from './Container';
import Loading from './Loading';
import Header from './Header';

var moment = require('moment');

const SOC_FIELDS = [
  'mode',
  'soc_on',
  'soc_off',
  'on_time',
  'off_time',
  'delay_off_minutes'
];

const NUMERIC_FIELDS = ['soc_on', 'soc_off', 'delay_off_minutes'];

const MODE_NORMAL = 'NORMAL';
const MODE_TIMED = 'TIMED';
const MODE_ALWAYS_ON = 'ALWAYS_ON';
const MODE_VEHICLE = 'VEHICLE';
const MODE_MANUAL = 'MANUAL';

const SOC_MODES = [MODE_MANUAL, MODE_NORMAL, MODE_TIMED];
const TIME_MODES = [MODE_TIMED, MODE_VEHICLE, MODE_MANUAL];
const DELAY_MODES = [MODE_MANUAL, MODE_VEHICLE];

const MODE_OPTIONS = [
  [MODE_NORMAL, 'Normal'],
  [MODE_TIMED, 'Timed'],
  [MODE_ALWAYS_ON, 'Always On'],
  [MODE_VEHICLE, 'Vehicle'],
  [MODE_MANUAL, 'Manual']
];

const MODES_VERBOSE = {
  NORMAL: 'When configuring a SupaBRCK that you will manually turn ON/OFF',
  TIMED: 'When configuring a SupaBRCK that is automatically turned ON/OFF at specific times using the device timer settings',
  ALWAYS_ON: 'When configuring a SupaBRCK that will need to be ON all the time',
  VEHICLE: 'When configuring a SupaBRCK that you will manually charge just like you charge a phone',
  MANUAL: 'When you want to be able to manually configure all power settings'
}

class Power extends Component {

  constructor(props) {
    super(props);
    this.state = {
      loaded: false,
      mode: '',
      soc_on: '',
      soc_off: '',
      on_time: '',
      off_time: '',
      delay_off_minutes: '',
      battery: {},
      errors: {}
    }
  }

  componentDidMount() {
    this.loadState();
  }

  loadState = (live) => {
    if (!this.state.working) {
      this.setState({ working: true });
      API.get_power_config(this.dataCallback, live);
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
        loaded: true
      });
      this.setState(res.body);
    }
  }

  handleInput = (e) => {
    var newState = {};
    newState[e.target.name] = e.target.value;
    this.setState(newState);
  }

  hardRefresh = (e) => {
    e.preventDefault();
    this.loadState(true);
  }

  handleModeChange = (e) => {
    this.setState({
      mode: e.target.value
    })
  }


  getModeVerbose = () => {
    return MODES_VERBOSE[this.state.mode];
  }
  
  handleConfigurePower = (e) => {
    e.preventDefault();
    var config = {}
    SOC_FIELDS.map((field) => {
      if(this.state[field] !== '') {
        config[field] = this.state[field];
        if (NUMERIC_FIELDS.indexOf(field) > -1) {
          config[field] = Number.parseInt(this.state[field], 10);
        }
      }
    })
    var payload = { power: config }
    this.setState({ working: true });
    API.configure_power(payload, this.configCallback);
  }

  configCallback = (res) => {
    this.setState({ working: false });
    if (!res.ok) {
        var errors = (res.status === 422) ? res.body.errors : {};
        this.setState({
            config_error: true,
            errors: errors
        });
    } else {
        this.setState({
            config_saved: true,
            config_error: false,
            errors: {}
        });
        this.setState(res.body);
    }
  }

  renderChargingStatus = (status) => {
    var classNames = "badge";
    if (status == "DISCHARGING") {
      classNames += " bg-red";
    } else if (status == "CHARGING"){
      classNames += " bg-green";
    } else {
      classNames += " bg-gray";
    }
    return <span className={classNames} style={{ width: '100px' }}>{ status }</span>
  }

  renderBatteryStatus = () => {
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="box">
            <div className="box-header">
              <h3 className="box-title">Battery</h3>
              <div className="box-tools">
                <div className="input-group input-group-sm" style={{ width: '150px' }}>
                  <div className="input-group-btn">
                    <button onClick={ this.hardRefresh } disabled={this.state.working} type="submit" className="btn btn-warning btn-flat pull-right">
                      <i className="fa fa-refresh"></i> Refresh
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div className="box-body table-responsive no-padding">
              <table className="table table-bordered table-condensed table-hover">
                <tbody>
                  <tr>
                    <th>Input Voltage</th>
                    <th>Input Current</th>
                    <th>SoC</th>
                  </tr>
                  <tr>
                    <td>{ this.state.battery.voltage || '0' }V</td>
                    <td>{ this.state.battery.charging_current || '0' }A</td>
                    <td>
                      { this.state.battery.battery_level || '0' }% { this.renderChargingStatus(this.state.battery.state) }
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  renderModeForm = () => {
    return (
      <div className="row" key="soc-mode">
        <div className="col-xs-12">
          <div className="box">
            <div className="box-header with-border">
              <h3 className="box-title">Configuration mode: {this.state.configured ? <span>{ this.state.mode }</span> : null} </h3>
            </div>
            <div className="box-body">
              <p>The purpose for which the device will be used.</p>
              <div className="row">
                <div className="col-xs-12 col-md-4 col-lg-2">
                  <div className={'form-group' + ' ' + (this.state.errors.mode ? 'has-error' : '') }>
                    <select name="mode"
                            value={ this.state.mode }
                            onChange={this.handleModeChange}
                            className="form-control fancy-select">
                              <option value={''}></option>
                      { MODE_OPTIONS.map((m, key) => {
                        return <option value={ m[0] } key={key}>{ m[1] }</option>
                      }) }
                    </select>
                    <label className="help-block text-danger">{ this.state.errors.mode }</label>
                  </div>
                </div>
                <div className="col-xs-12 col-md-4 col-lg-2 col-md-offset-4 col-lg-offset-8">
                </div>
              </div>
              <div className="row">
                  <div className="col-xs-12">
                      {(this.state.mode)
                       ? <p className="text-orange text-bold">{ this.getModeVerbose() }</p>
                       : <p className="text-muted text-bold">No mode selected</p>
                      }
                  </div>
              </div>
            </div>
          </div>
        </div>
     </div>
    );
  }

  renderSOCForm = () => {
    return (
      <div className="col-md-6">
        <div className="box">
          <div className="box-header with-border">
            <h3 className="box-title">SOC Settings</h3>
          </div>
          <div className="box-body">
            <p>The device turns off when the charge goes below the
              <strong>SOC OFF</strong> setting and only turns on after the charge level is equivalent to the
              <strong>SOC ON </strong>settings</p>
            <div className="row">
              <div className="col-md-4">
                <div className="bootstrap-timepicker">
                  <div className="form-group">
                    <label>TURN OFF SOC:</label>
                    <div className={'input-group' + ' ' + (this.state.errors.soc_off ? 'has-error' : '') }>
                      <input 
                        name="soc_off"
                        value={ this.state.soc_off }
                        onChange={ this.handleInput }
                        type="number"
                        min="1"
                        max="99"
                        className="form-control" />
                        <span className="input-group-addon"><i className="fa fa-percent"></i></span>
                    </div>
                    <label className="help-block text-danger">{ this.state.errors.soc_off }</label>
                  </div>
                </div>
              </div>
              <div className="col-md-4 col-md-offset-3">
                <div className="bootstrap-timepicker">
                  <div className="form-group">
                    <label>TURN ON SOC:</label>
                    <div className={'input-group' + ' ' + (this.state.errors.soc_on ? 'has-error' : '') }>
                      <input 
                        name="soc_on"
                        value={ this.state.soc_on }
                        onChange={ this.handleInput }
                        type="number"
                        min="1"
                        max="99"
                        className="form-control" />
                        <span className="input-group-addon"><i className="fa fa-percent"></i></span>
                    </div>
                    <label className="help-block text-danger">{ this.state.errors.soc_on }</label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }


  renderTimeOptions = () => {
    var timeOptions = [];
    for (let index = 0; index < 24; index++) {
      var m0 = moment({ hour: index, minute: 0});
      var m1 = moment({ hour: index, minute: 30 });
      var opt0 = m0.format('HH:mm');
      var opt1 = m1.format('HH:mm');
      timeOptions.push(<option value={ opt0 }>{ opt0 }</option>);
      timeOptions.push(<option value={ opt1 }>{ opt1 }</option>);
    }
    return timeOptions;
  }

  renderTimeForm = () => {
    return (
      <div className="col-md-6">
        <div className="box">
          <div className="box-header with-border">
            <h3 className="box-title">Turn ON/OFF Time</h3>
          </div>
          <div className="box-body">
            <p>Time when the device automatically turns ON or OFF</p>

            <div className="row">
              <div className="col-md-5">
                <div className="bootstrap-timepicker">
                  <div className="form-group">
                    <label>TURN ON TIME:</label>
                    <div className={'input-group' + ' ' + (this.state.errors.on_time ? 'has-error' : '') }>
                      <select name="on_time"
                              value={ this.state.on_time }
                              onChange = { this.handleInput }
                              className="form-control fancy-select"
                            >
                        { this.renderTimeOptions() }
                      </select>
                      <div className="input-group-addon">
                        <i className="fa fa-clock-o"></i>
                      </div>
                    </div>
                    <label className="help-block text-danger">{ this.state.errors.on_time }</label>
                  </div>
                </div>
              </div>
              <div className="col-md-5 col-md-offset-2">
                <div className="bootstrap-timepicker">
                  <div className="form-group">
                    <label>TURN OFF TIME:</label>
                    <div className={'input-group' + ' ' + (this.state.errors.off_time ? 'has-error' : '') }>
                    <select name="off_time"
                            value={ this.state.off_time }
                            onChange = { this.handleInput }
                            className="form-control fancy-select"
                          >
                      { this.renderTimeOptions() }
                    </select>
                    <div className="input-group-addon">
                      <i className="fa fa-clock-o"></i>
                    </div>
                    </div>
                    <label className="help-block text-danger">{ this.state.errors.off_time }</label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  renderDelayForm = () => {
    return (
      <div className="row">
        <div className="col-md-6">
            <div className="box">
                <div className="box-header with-border">
                    <h3 className="box-title">Delayed Switch Off Timer</h3>
                </div>
                <div className="box-body">
                    <p>When not charging, how long should the device stay on before automatically shutting down</p>
                    <div className="row">
                        <div className="col-md-6">
                            <div className="form-group">
                              <div className={'input-group' + ' ' + (this.state.errors.soc_off ? 'has-error' : '') }>
                                <input
                                name="delay_off_minutes"
                                value={ this.state.delay_off_minutes }
                                onChange={ this.handleInput }
                                type="number"
                                min="1"
                                max="60"
                                className="form-control"
                                placeholder="Units in minutes (e.g 5)" />
                              </div>
                              <label className="help-block text-danger">{ this.state.errors.delay_off_minutes }</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    );
  }


  renderDialog = () => {
    return (
      <div className="modal fade" id="modal-confirm">
        <div className="modal-dialog">
            <div className="modal-content">
                <div className="modal-header">
                    <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span></button>
                    <h4 className="modal-title">Are you sure?</h4>
                </div>
                <div className="modal-body">
                    <p>You are about to configure your SupaBRCK as <strong>{ this.state.mode }</strong></p>
                </div>
                <div className="modal-footer">
                    <button type="button" className="btn btn-default pull-left" data-dismiss="modal">Cancel</button>
                    <a href="." onClick={ this.handleConfigurePower } className="btn btn-primary" data-dismiss="modal">Confirm</a>
                </div>
            </div>
        </div>
    </div>
    );
  }

  renderSubmit = () => {
    return (
      <div className="row">
          <div className="col-xs-3 ">
              <button type="button"
                className="btn btn-block btn-primary btn-lg"
                data-toggle="modal" 
                data-target="#modal-confirm">Save</button>
          </div>
      </div>
    );
  }

  renderMessages = () => {
    const rootError = this.state.errors.soc || "Review errors below";
    return (
      <div className="row">
        <div className="col-xs-12">
          {(this.state.config_saved
            ? <AlertSuccess message={"Your power settings have been saved successfully."} />
            : null)}
          {(this.state.config_error
            ? <AlertError title={"Could not configure device"}
                errors={[ rootError ]} />
            : null)}
        </div>
      </div>
    )
  }

  checkModes = (modes) => {
    return modes.indexOf(this.state.mode) >= 0;
  }

  renderBody = () => {
    return (
      <div className="content container-fluid">
        { this.renderDialog() }
        { this.renderBatteryStatus() }
        { this.renderMessages() }
        { this.renderModeForm()  }
        <div className="row">
          { this.checkModes(SOC_MODES) ? this.renderSOCForm() : null }
          { this.checkModes(TIME_MODES) ? this.renderTimeForm() : null }
        </div>
        { this.checkModes(DELAY_MODES) ? this.renderDelayForm() : null }
        { this.state.mode ? this.renderSubmit() : null}
      </div>
    );
  }

  render() {
    return (
      <Container>
        <div>
          <Header>Power Management</Header>
          {(this.state.loaded)
          ? this.renderBody()
          : <Loading message="Loading power settings" />}
        </div>
      </Container>
    );
  }
}

export default Power;
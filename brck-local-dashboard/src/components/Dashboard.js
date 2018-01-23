import React, { Component } from 'react';

import Header from './Header';

class Dashboard extends Component {

  renderBody = () => {
    return(
      <div class="content container-fluid">
        <div class="row connection-dash-stats">
          <div class="col-md-6">
            <div class="info-box">
              <span class="info-box-icon bg-orange">
                <img alt="ethernet" src="/dist/img/icons/icon_ethernet-white.svg" class="center-block ethernet-icon"/>
              </span>
              <div class="info-box-content">
                <h4>CONNECTION SIGNAL</h4>
                <p>Ethernet</p>
              </div>
            </div>
          </div>


          <div class="col-md-6">
            <div class="info-box">
              <span class="info-box-icon bg-green">
                <i class="fa fa-battery-0 big-icon"/>
              </span>
              <div class="info-box-content">
                <h4>CHARGE LEVEL</h4>
                <p>100%</p>
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
                      <span class="speed">20.6 KB/s</span> 
                      <br/>
                      <span class="traffic">Upload</span>
                    </li>
                    <li>
                      <i class="fa fa-chevron-circle-down"></i>
                      <span class="speed">20.6 KB/s</span>
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
                  <p>23</p>
                </div>
              </div>
            </div>
          </div>
        </div>
    );
  }

  render() {
    return [
      <Header>Dashboard</Header>,
      this.renderBody()
    ];
  }
}

export default Dashboard;

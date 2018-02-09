import React, { Component } from 'react';

import { NavLink, Link } from 'react-router-dom';

import LogoMini from '../media/brck-logo-mini.svg';
import LogoLarge from '../media/brck-logo-lg.svg';

class Container extends Component {

  renderHeader = () => {
    return (
      <header className="main-header">
        <a href="/" className="logo">
          <span className="logo-mini"><img alt="BRCK" src={ LogoMini } /></span>
          <span className="logo-lg"><img alt="BRCK" src={ LogoLarge } /></span>
        </a>


        <nav className="navbar navbar-static-top">
          <a href="#" className="sidebar-toggle" data-toggle="push-menu" role="button">
            <span className="sr-only">Toggle navigation</span>
          </a>
          <div className="navbar-custom-menu">
            <ul className="nav navbar-nav">
              <li className="dropdown user user-menu">
                <a href="#" className="dropdown-toggle" data-toggle="dropdown">
                  <span className="fa fa-user" />
                  <span className="hidden-xs">Admin</span>
                </a>
                <ul className="dropdown-menu">
                  <li className="user-footer">
                    <div className="pull-right">
                      <Link 
                        to="/change-password"
                        className="btn btn-flat btn-default btn-block">
                        Change Password
                      </Link>
                      <Link 
                        to="/logout"
                        className="btn btn-warning btn-flat btn-block">
                        Sign Out
                      </Link>
                    </div>
                  </li>
                </ul>
              </li>   
            </ul>
          </div>
        </nav> 
      </header>
    );
  }

  renderSideBar = () => {
    return (
      <aside className="main-sidebar">
          <section className="sidebar">
            <ul className="sidebar-menu" data-widget="tree">
              {/* <li className="treeview main-dropdown">
                <a href="#">
                  <b className="caret"></b>
                  <span className="main-dropdown-title">SupaBRCK DASHBOARD</span>      
                </a>
              </li> */}
    
              <li>
                <NavLink to="/dashboard">
                  <i className="fa fa-calendar"></i>
                  <span>Dashboard</span>
                  <span className="pull-right-container" />
                </NavLink>
              </li>              
              <li>
                <NavLink to="/connect">
                  <i className="fa fa-signal"></i>
                  <span>Connectivity</span>
                  <span className="pull-right-container" />
                </NavLink>
              </li>              
              <li>
                <NavLink to="/power">
                  <i className="fa fa-power-off"></i>
                  <span>Power</span>
                  <span className="pull-right-container" />
                </NavLink>
              </li>              
            </ul>
          </section>
        </aside>
    );
  }

  renderFooter = () => {
    return (
      <footer className="main-footer">
        <div className="pull-right hidden-xs">
          <b>Version</b> 2.0
        </div>
        <strong>Copyright &copy; 2017 <a href="https://www.brck.com">BRCK INC</a>.</strong> All rights reserved.
      </footer>
    );  
  }

  render() {
    return(
      <div className="wrapper" style={{height: '100%', minHeight: '100%'}}>
        { this.renderHeader() }
        { this.renderSideBar() }
        <div className="content-wrapper">
          { this.props.children }
        </div>
        { this.renderFooter() }
      </div>
    );
  }
}

export default Container;
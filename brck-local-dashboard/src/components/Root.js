import React, {Component} from 'react';

import {
    BrowserRouter as Router,
    Route,
    NavLink
} from 'react-router-dom';

import Dashboard from './Dashboard';
import Connections from './Connections';

class Root extends Component {

  render() {
    return (
      <Router>
        <div className="wrapper">
          <header className="main-header">
              <a href="/" className="logo">
                <span className="logo-mini"><img src="/dist/img/brck-logo-mini.svg" /></span>
                <span className="logo-lg"><img src="/dist/img/brck-logo-lg.svg"/></span>
              </a>


              <nav className="navbar navbar-static-top" role="navigation">
                <a href="#" className="sidebar-toggle" data-toggle="push-menu" role="button">
                  <span className="sr-only">Toggle navigation</span>
                </a>
                <div className="navbar-custom-menu">
                  <ul className="nav navbar-nav">
                    <li className="dropdown user user-menu">
                      <a href="#" className="dropdown-toggle" data-toggle="dropdown">
                        <img src="/dist/img/user2-160x160.jpg" className="user-image" alt="User Image"/>
                        <span className="hidden-xs">Admin</span>
                      </a>
                      <ul className="dropdown-menu">
                        <li className="user-header">
                          <img src="/dist/img/user2-160x160.jpg" className="img-circle" alt="User Image"/>
                        </li>
                        <li className="user-footer">
                          <div className="pull-left">
                            <a href="#" className="btn btn-default btn-flat">Profile</a>
                          </div>
                          <div className="pull-right">
                            <a href="#" className="btn btn-default btn-flat">Sign out</a>
                          </div>
                        </li>
                      </ul>
                    </li>   
                  </ul>
                </div>
              </nav>   


          </header>


        <aside className="main-sidebar">
            <section className="sidebar">
              <ul className="sidebar-menu" data-widget="tree">
                <li className="treeview main-dropdown">
                  <a href="#">
                    <b className="caret"></b>
                    <span className="main-dropdown-title">SupaBRCK DASHBOARD</span>      
                  </a>
                </li>
      
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
                  <a href="#">
                    <i className="fa fa-list-alt"></i>
                    <span>Content</span>
                    <span className="pull-right-container">
                  </span>
                  </a>
                </li>
      
                <li>
                  <a href="#">
                    <i className="fa fa-tv"></i>
                    <span>Compute</span>
                    <span className="pull-right-container">
                  </span>
                  </a>
                </li>
                
                <li>
                  <a href="#">
                  <i className="fa fa-download"></i>
                    <span>Compute</span>
                    <span className="pull-right-container">
                  </span>
                  </a>
                </li>
              </ul>
            </section>
          </aside>

          <div className="content-wrapper">
              <Route exact path="/dashboard" component={Dashboard} />
              <Route exact path="/connect" component={Connections} />
          </div>

          <footer className="main-footer">
              <div className="pull-right hidden-xs">
                <b>Version</b> 2.0
              </div>
              <strong>Copyright &copy; 2017 <a href="https://www.brck.com">BRCK INC</a>.</strong> All rights reserved.
          </footer>
        
      </div>
    </Router>
    );
  }
}


export default Root;
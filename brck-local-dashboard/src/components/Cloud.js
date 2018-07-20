import React, { Component } from 'react';
import API from '../utils/API'
import Header from './Header'


class Cloud extends Component {
  constructor(props) {
    super(props);
      this.state = {
        retailMode: 1,
        connected: false,
        setupLink: ""
      }
  }

  setDeviceMode = (err, res) => {
    if (res.ok){
      var retail;
      if (res.body.mode == "RETAIL"){
        retail = 1;
      } else {
        retail = 0;
      }
      this.setState({
        retailMode: retail,
        connected: res.body.connected,
        setupLink: res.body.setup_link
      });

    }
  }

  componentDidMount(){
    API.get_device_mode(this.setDeviceMode);
  }
  render() {
    return (
      <div>
        {(this.state.connected)
         ? <div>
             <Header>Connectivity</Header>
             <div className="container-fluid top-space-30">
               <div class="box box-default">
                 <div class="box-header with-border">
                   <h3 class="box-title">SupaBRCK Cloud</h3>
                 </div>
                 <div class="box-body">
                   <p> Register and manage your SupaBRCK device on the cloud</p> 
                   <a href={this.state.setupLink} class="btn btn-success" target="_blank">Go to Cloud</a>
                 </div>
               </div>
             </div>
           </div>
         : <p></p>
        }
      </div>
    );
  }
}

export default Cloud;

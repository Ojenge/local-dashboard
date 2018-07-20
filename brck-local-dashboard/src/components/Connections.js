import React, { Component } from 'react';

import Container from './Container'
import SIMConnections from './SIM'
import Ethernet from './Ethernet'
import Cloud from './Cloud'


class Connections extends Component {
  render() {
    return (
      <Container>
         <Cloud />
         <SIMConnections />
         <Ethernet />   
      </Container>
    );
  }
}

export default Connections;

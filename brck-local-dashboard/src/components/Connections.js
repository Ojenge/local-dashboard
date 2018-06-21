import React, { Component } from 'react';

import Container from './Container'
import SIMConnections from './SIM'
import Ethernet from './Ethernet'


class Connections extends Component {
  render() {
    return (
      <Container>
         <SIMConnections />
         <Ethernet />   
      </Container>
    );
  }
}

export default Connections;

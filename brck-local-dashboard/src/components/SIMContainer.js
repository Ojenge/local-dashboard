import React, { Component } from 'react';

import Container from './Container.js'
import SIMConnections from './SIM'

class SIMConnectionsContainer extends Component {
  render() {
    return (      
      <Container>
        <SIMConnections />
      </Container>
    );
  }
}

export default SIMConnectionsContainer;

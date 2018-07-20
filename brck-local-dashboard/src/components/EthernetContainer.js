import React, { Component } from 'react';

import Container from './Container'
import Ethernet from './Ethernet'


class EthernetContainer extends Component {
  render() {
    return (      
      <Container>
        <Ethernet />
      </Container>
    );
  }
}

export default EthernetContainer;

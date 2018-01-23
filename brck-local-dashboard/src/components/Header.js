import React, { Component } from 'react';

class Header extends Component {
  render() {
    return (
      <section class="content-header">
        <h1> {this.props.children} </h1>
      </section>
    );
  }
}

export default Header;

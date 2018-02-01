import React, { Component } from 'react';

class Loading extends Component {
  
  constructor(props) {
      super(props);
      this.state = {
          message: this.props.message || "Working"
      }
  }

  render() {
      return (
        <div className="login-box">
            <div className="login-logo">
            </div>
            <div className="login-box-body">
                <div class="spinner">
                    <span />
                </div>
                <p className="login-box-msg">{ this.state.message }</p>
            </div>
        </div>

      );
  }
}

export default Loading;

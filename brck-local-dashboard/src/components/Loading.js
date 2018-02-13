import React, { Component } from 'react';

class Loading extends Component {
  
  constructor(props) {
      super(props);
      this.state = {
          message: this.props.message || "Loading..."
      }
  }

  render() {
      return (
        <div className="login-box">
            <div className="login-logo">
            </div>
            <div>
                <div className="spinner">
                    <span />
                </div>
                <p className="login-box-msg text-yellow">{ this.state.message }</p>
            </div>
        </div>

      );
  }
}

export default Loading;

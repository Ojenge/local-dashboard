import React, { Component } from 'react';

class Loading extends Component {
  
  constructor(props) {
      super(props);
      this.state = {
          message: this.props.message || "Loading..."
      }
  }

  render() {
      const textClass = 'login-box-msg ' +  (this.props.textClass || 'text-black');
      return (
        <div className="login-box">
            <div className="login-logo">
            </div>
            <div>
                <div className="spinner">
                    <span />
                </div>
                <p className={textClass}>{ this.state.message }</p>
            </div>
        </div>

      );
  }
}

export default Loading;

import React, { Component } from 'react';

class Loading extends Component {
  render() {
    return (
        <div className="content container-fluid">
            <div className="row">
                <div className="col-xs-12">
                    <div className="alert alert-warning text-center">
                        <img src="/bower_components/ckeditor/skins/moono-lisa/images/spinner.gif" alt="Loading" />
                        <h4>{ this.props.message }</h4>
                    </div>
                </div>
            </div>
        </div>
    );
  }
}

export default Loading;

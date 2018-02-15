import React from 'react';

export const AlertInfo = props => {
  return (
    <div className="alert alert-info alert-dismissible">
      <button type="button" className="close" data-dismiss="alert" aria-hidden="true">×</button>
      { props.message }
    </div>
  );
}

export const AlertSuccess = props => {
  return (
    <div className="alert alert-success alert-dismissible">
      <button type="button" className="close" data-dismiss="alert" aria-hidden="true">×</button>
      { props.message }
    </div>
  );
}

export const AlertWarning = props => {
  return (
    <div className="alert alert-danger alert-dismissible">
      <button type="button" className="close" data-dismiss="alert" aria-hidden="true">×</button>
      { props.message }
    </div>
  );
}

export const AlertError = props => {
  return (
    <div className="alert alert-danger alert-dismissible">
      <button type="button" className="close" data-dismiss="alert" aria-hidden="true">×</button>
      <h4>{ props.title }</h4>
      <ul>
        {props.errors.map((err, key) => 
          <li key={key}>{ err }</li>
         )}
      </ul>
  </div>
  );
}
import React from 'react';
import '../App.css';

function Location(props) {
  const {
    name = 'Location Name',
    score = '',
    image = '/assets/imgs/img1.png', // default to an existing image in public/assets/imgs
  } = props || {};

  const bg = image ? `url(${image})` : 'none';

  return (
    <div
      className="location-item location-card card mb-3 clickable"
      role="button"
      tabIndex={0}
      style={{ backgroundImage: bg }}
    >
      <div className="location-badge">{props.score}</div>
      <div className="location-gradient" />
      <div className="location-name">{props.name}</div>
    </div>
  );
}

export default Location;
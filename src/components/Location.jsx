import React from 'react';
import '../App.css';

// 1. Destructure props from the single 'props' object
function Location({ ID, name, score, image, onSelect }) {

  const bg = image ? `url(${image})` : 'none';

  // 2. Return the JSX element directly
  return (
    <div
      className="location-item location-card card mb-3 clickable"
      role="button"
      tabIndex={0}
      // 3. The 'style' prop takes an object, which you did correctly
      style={{ backgroundImage: bg }}
      // 4. Use the React 'onClick' handler
      onClick={() => {
        // Call the onSelect function passed from the parent
        if (onSelect) {
          onSelect(ID);
        }
      }}
    >
      <div className="location-badge">{score}%</div>
      <div className="location-gradient" />
      <div className="location-name">{name}</div>
    </div>
  );
}

export default Location;
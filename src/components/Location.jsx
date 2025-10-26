import '../App.css';

function Location() {
  return (
    <div className="location-item location-card card mb-3">
      <div className="card-body">
        <h5 className="card-title">Location Name</h5>
        <p className="card-text">1234 Donation St.<br />City, State, ZIP</p>
        <p className="card-text"><small className="text-muted">Distance: 2.5 miles</small></p>
      </div>
    </div>
  );
}

export default Location; 
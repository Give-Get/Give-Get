import React from 'react';
import Location from './Location';
import Donation from './Donation';
import { useNavigate } from 'react-router-dom';
import '../App.css';

export default function Main() {
  const navigate = useNavigate();
  function handleLogout() {
    localStorage.removeItem('auth');
    navigate('/login', { replace: true });
  }

  return (
    <div className="main-container">
      <aside className="sidebar">
        <div className="sidebar-top">
          <h4 className="mb-3">What items are you donating?</h4>
          <button className="btn btn-primary">+ Add item</button>
          <div className="donation-list pt-3">
            <Donation />
            <Donation />
            <Donation />
          </div>
        </div>

        <div className="sidebar-bottom mt-auto">
          <button className="btn btn-outline-secondary w-100" onClick={handleLogout}>Logout</button>
        </div>
      </aside>

      <main className="main-content">
        <div className="content-column">
          <div className="media-wrap">
            <div className="media-map">
              <div className="media-placeholder">Google Maps Placeholder</div>
            </div>
          </div>

          <div className="horizontal-bar card">
            <div className="card-body">
              <h4 className="mb-2">Matched Locations</h4>
              <div className="location-list">
                <Location />
                <Location />
                <Location />
                <Location />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
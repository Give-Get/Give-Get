import React, { useState } from 'react';
import Location from './Location';
import Donation from './Donation';
import AddItemForm from './AddItemForm';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import GoogleMapDisplay from './GoogleMapDisplay';

export default function Main() {
  const navigate = useNavigate();
  const [donations, setDonations] = useState([]);

  function handleLogout() {
    localStorage.removeItem('auth');
    navigate('/login', { replace: true });
  }

  async function addDonation(donation) {
    donation.itemName="Sample Item";
    donation.quantity=1;
    donation.size="Medium";
    donation.category="Clothing";
    donation.description="A sample description of the donated item.";
    setDonations([...donations, donation]);
  }

  return (
    <div className="main-container">
      <aside className="sidebar">
        <div className="sidebar-top">
          <h4 className="mb-3">What items are you donating?</h4>
          <button
          className="btn btn-primary add-item-button"
          onClick={addDonation}>+ Add item</button>
        </div>
        <div className="donation-list mx-4">
          <AddItemForm />
          {donations.map(donation => (
            <Donation 
              key={donation.id}
              itemName={donation.itemName}
              quantity={donation.quantity}
              size={donation.size}
              category={donation.category}
              description={donation.description}
            />
          ))}
        </div>

        <div className="sidebar-bottom mt-auto">
          <button className="btn btn-outline-secondary w-100" onClick={handleLogout}>Logout</button>
        </div>
      </aside>

      <main className="main-content">
        <div className="content-column">
          <div className="media-wrap">
            <div className="media-map">
              <GoogleMapDisplay />
            </div>
          </div>

          <div className="horizontal-bar card">
            <div className="card-body">
              <h4 className="mb-2">Top Matches within 1 mi</h4>
              <div className="location-list pt-2">
                <Location 
                    name="Location 1"
                    score={"96%"}
                    />
                <Location 
                    name="Location 2"
                    score={"85%"}/>
                <Location 
                    name="Location 3"
                    score={"91%"}/>
                <Location 
                    name="Location 4"
                    score={"89%"}/>
                <Location 
                    name="Location 5"
                    score={"82%"}/>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
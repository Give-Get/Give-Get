import React, { useState, useEffect, useCallback } from 'react';
import Location from './Location';
import Donation from './Donation';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import GoogleMapDisplay from '../GoogleMapDisplay';

const locations = {
  "4": {
    "type": {"shelter": true, "charity": false},
    "EIN": 6,
    "name": "Shelter1",
    "address": "123 Shelter St",
    "location": { "lat": 0, "lng": 0},
    "ammenities": {
        "accessible": false,
        "lgbtq_only": false,

        "male_only": false,
        "female_only": false,
        "all_gender": false,
        "pet_friendly": false,
        "languages": ["english"],
        "family_rooming": false,
        "beds_available": 10,
        "medical_support": true,
        "counseling_support": true,
        "fees": 0,
        "age_minimum": 0,
        "age_maximum": 18,
        "veteran_only": true,
        "immigrant_only": true,
        "refugee_only": true,
        "good_criminal_record_standing": false,
        "sobriety_required": true,
        "showers": true,
        "id_required": false
    },
    "needs": [
      {"category":"food", "item": "canned beans", "needed": 200, "have": 150, "urgency": "high"},
      {"category":"clothing", "item": "jackets", "needed": 50, "have": 30, "urgency": "low"}
    ],
    "hours": {
      "monday": "0000-2359",
      "tuesday": "0000-2359",
      "wednesday": "0000-2359",
      "thursday": "0000-2359",
      "friday": "0000-2359",
      "saturday": "0000-2359",
      "sunday": "0000-2359"
    },
    "description": "Shelter for homeless",
    "contact": {
      "phone": "123-456-7890",
      "email": "shelteremail@domain.tld",
      "website": "shelterwebsite.com"
    },
    "verified": true,
    "timestamp": ""
  },
  "1": {
    "type": {"shelter": false, "charity": true},
    "EIN": 0,
    "name": "Centre County Food Bank",
    "address": "123 Main St, State College, PA",
    "location": { "lat": 40.793, "lng": -77.86 },
    "ammenities": {},
    "needs": [
      {"category":"food", "item": "canned beans", "needed": 200, "have": 150, "urgency": "high"},
      {"category":"clothing", "item": "jackets", "needed": 50, "have": 30, "urgency": "low"}
    ],
    "hours": {
      "monday": "0000-2359",
      "tuesday": "0000-2359",
      "wednesday": "0000-2359",
      "thursday": "0000-2359",
      "friday": "0000-2359",
      "saturday": "0000-2359",
      "sunday": "0000-2359"
    },
    "description": "Local non-profit collecting food and clothing for low-income families.",
    "contact": {
      "phone": "814-555-1234",
      "email": "info@foodbank.org",
      "website": "https://foodbank.org"
    },
    "verified": true,
    "timestamp": "2025-10-25T03:00:00Z"
  }
}

export default function Main() {
  const [userLocation, setUserLocation] = useState({ lat: 40.8148, lng: -77.8653 });

  // Tracks which location card is clicked/highlighted
  const [selectedLocationId, setSelectedLocationId] = useState(null);

  // Tracks which location to actively route to on the map
  const [routeToId, setRouteToId] = useState(null);

  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem('auth');
    navigate('/login', { replace: true });
  }

// --- Add event handlers ---

  // This sets the *selected* location when a user clicks on a card
  const handleSelectLocation = useCallback((id) => {
    setSelectedLocationId(id);
    setRouteToId(id);
  }, []);


  // This clears the route from the map
  const handleClearRoute = () => {
    setSelectedLocationId(null)
    setRouteToId(null);
  };

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error("Error getting user location:", error);
        }
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
    }
  }, []); // Runs once on component mount

  console.log(userLocation)


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
              <GoogleMapDisplay routeToId={routeToId}
              locations={locations}
              userLocation={userLocation}
              onMarkerClick={handleSelectLocation}
              onInfoClose={handleClearRoute}/>
            </div>
          </div>

          <div className="horizontal-bar card">
            <div className="card-body">
              <h4 className="mb-2">Matched Locations</h4>
              <div className="location-list">
                  <Location />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
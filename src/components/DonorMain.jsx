import React, { useState, useEffect, useCallback } from 'react';
import Location from './Location';
import Donation from './Donation';
import AddItemForm from './AddItemForm';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import GoogleMapDisplay from './GoogleMapDisplay';

async function getSupplyMatches(requestData) {
  // Use your Render URL from environment variables
  // Make sure to create a .env.local file with REACT_APP_API_URL=https://your-service-name.onrender.com
  const API_URL = `${process.env.REACT_APP_API_URL}/api/match-supplies`;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData)
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Something went wrong");
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch matches:", error);
    throw error;
  }
}

export default function Main() {
  const [userLocation, setUserLocation] = useState({ lat: 40.8148, lng: -77.8653 });

  // Tracks which location card is clicked/highlighted
  const [selectedLocationId, setSelectedLocationId] = useState(null);

  // Tracks which location to actively route to on the map
  const [routeToId, setRouteToId] = useState(null);

  const navigate = useNavigate();
  const [donations, setDonations] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);

  const [radius, setRadius] = useState(1);
  const [locations, setLocations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  useEffect(() => {
    // Don't run if we don't have the user's location yet
    if (!userLocation) return;

    const fetchMatches = async () => {
      setLoading(true);
      setError(null);
     
      // Format the 'donations' state to match the API's 'donor_items' schema
      const donorItemsPayload = (donations && donations.length > 0)
        ? { items: donations.map(d => ({
              category: d.category,
              item: d.itemName,
              quantity: d.quantity
            })) }
        : null;

      const requestData = {
        location: userLocation,
        radius: parseInt(radius, 10),
        donor_items: donorItemsPayload
      };

      try {
        const data = await getSupplyMatches(requestData);
        // Store the ranked_organizations object in your 'locations' state
        setLocations(data.ranked_organizations); 
      } catch (err) {
        setError(err.message || "An unknown error occurred.");
        setLocations(null); // Clear old results on error
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
    
  // Re-run this effect if any of these three dependencies change
  }, [donations, radius, userLocation]);


  async function addDonation(donation) {
    // normalize/ensure fields and create an id
    const newDonation = {
      id: Date.now(),
      itemName: donation.itemName || 'Unnamed item',
      quantity: Number(donation.quantity) || 1,
      size: donation.size || '',
      category: donation.category || '',
      description: donation.description || ''
    };

    setDonations(prev => [...prev, newDonation]);
    // hide the form and return to the list view
    setShowAddForm(false);
  }

  async function deleteDonation(id) {
    setDonations(prev => prev.filter(donation => donation.id !== id));
  }

  // Derive the selected location object for convenience
  const selectedLocation =
  selectedLocationId && locations
    ? locations[selectedLocationId]
    : null;

  return (
    <div className="main-container">
<aside className="sidebar">
        <div className="sidebar-top">
          <h4 className="mb-3">What items are you donating?</h4>
          <div style={{ position: 'relative', width: '100%' }}>
            {showAddForm ? (
              <AddItemForm onAdd={addDonation} onBack={() => setShowAddForm(false)}/>
            ) : (
              <button
                className="btn btn-primary add-item-button"
                onClick={() => setShowAddForm(true)}>
                + Add item
              </button>
            )}
          </div>
        </div> 

        <div className="donation-list mx-4">
          {!showAddForm && (
            donations.map(donation => (
              <Donation 
                key={donation.id}
                itemName={donation.itemName}
                quantity={donation.quantity}
                size={donation.size}
                category={donation.category}
                description={donation.description}
                onClick={() => deleteDonation(donation.id)}
              />
            ))
          )}
        </div>

        <div className="sidebar-bottom mt-auto">
          <button className="btn btn-outline-secondary w-100" onClick={handleLogout}>Logout</button>
        </div>
      </aside>

      <main className="main-content">
        <img
          src="/assets/home.svg"
          alt="Home"
          onClick={() => navigate('/')}
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            zIndex: 1000,
            width: '24px',
            height: '24px',
            cursor: 'pointer',
          }}
        />
        <div className="content-column">
          <div className="media-wrap">
            <div className="media-map">
              <GoogleMapDisplay
              routeToId={routeToId}
              locations={locations}
              userLocation={userLocation}
              selectedLocationId={selectedLocationId}
              onMarkerClick={handleSelectLocation}
              onInfoClose={handleClearRoute}
              />
            </div>
          </div>
        </div>
      </main>

      <div className="horizontal-bar">
        <div className="card-body">
          {selectedLocation ? (
            <div className="selected-location d-flex align-items-stretch gap-3 pt-3">
              <img
                src={'/assets/imgs/img1.png'}
                alt={selectedLocation.name}
                className="selected-location-img"
              />
              <div className="selected-location-details flex-grow-1">
                <div className="d-flex align-items-start justify-content-between mb-2">
                  <div>
                    <h4 className="mb-1">{selectedLocation.name}</h4>
                    <div className="text-muted small">
                      {selectedLocation.address}
                        {" • "}
                      {selectedLocation?.type?.shelter ? 'Shelter' : selectedLocation?.type?.charity ? 'Charity' : 'Organization'}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleClearRoute}
                    className="back-arrow-btn"
                    aria-label="Back to matches"
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: '4px 8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      cursor: 'pointer',
                      flexShrink: 0,
                      color: '#adb5bd',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                    }}
                  >
                    <span>Back</span>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </button>
                </div>

                {selectedLocation.description && (
                  <p className="mb-2">{selectedLocation.description}</p>
                )}

                {Array.isArray(selectedLocation.needs) && selectedLocation.needs.length > 0 && (
                  <div className="mb-2">
                    <strong className="me-2">Top needs:</strong>
                    <span className="selected-location-needs">
                      {selectedLocation.needs.slice(0, 3).map((need, idx) => (
                        <span key={idx} className="need-chip">
                          {need.item}{need.needed ? ` (${Math.max(need.needed - (need.have || 0), 0)} needed)` : ''}
                        </span>
                      ))}
                    </span>
                  </div>
                )}

                {selectedLocation.contact && (
                  <div className="selected-location-contact d-flex flex-wrap gap-3 mt-2">
                    {selectedLocation.contact.phone && (
                      <span className="contact-item text-nowrap">
                        <span className="contact-icon">●</span> {selectedLocation.contact.phone}
                      </span>
                    )}
                    {selectedLocation.contact.email && (
                      <span className="contact-item text-nowrap">
                        <span className="contact-icon">✉</span> {selectedLocation.contact.email}
                      </span>
                    )}
                    {selectedLocation.contact.website && (
                      <a
                        className="contact-item text-nowrap"
                        href={selectedLocation.contact.website}
                        target="_blank"
                        rel="noreferrer noopener"
                      >
                        <span className="contact-icon">◉</span> Website
                      </a>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <>
              <h4 className="mt-2 d-flex align-items-center">
              Top Matches within&nbsp;
              <select
                value={radius}
                onChange={(e) => setRadius(Number(e.target.value))}
                className="radius-select"
              >
                <option value={1}>1 mi</option>
                <option value={5}>5 mi</option>
                <option value={10}>10 mi</option>
                <option value={20}>20 mi</option>
                <option value={50}>50 mi</option>
              </select>
            </h4>
              <div className="location-list pt-2">
                {locations && Object.keys(locations).map(locationId => {
                  const location = locations[locationId];
                  
                  return (
                    <Location 
                      key={locationId}
                      name={location.name}
                      score={location.score} 
                      image={'/assets/imgs/img1.png'}
                      ID = {locationId}
                      onSelect={handleSelectLocation}
                    />
                  );
                })}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
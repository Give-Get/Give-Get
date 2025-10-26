import React, { useState, useEffect, useCallback } from 'react';
import Location from './Location';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import GoogleMapDisplay from './GoogleMapDisplay';

async function getPeopleMatches(requestData) {
  const API_URL = process.env.REACT_APP_API_URL 
    ? `${process.env.REACT_APP_API_URL}/api/match-people`
    : 'http://localhost:8000/api/match-people'; // Fallback to localhost

  console.log("Sending request to:", API_URL);
  console.log("Request payload:", JSON.stringify(requestData, null, 2));

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error Response:", errorData);
      throw new Error(JSON.stringify(errorData.detail || errorData, null, 2));
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch matches:", error);
    throw error;
  }
}

export default function InNeedMain() {
  const [userLocation, setUserLocation] = useState({ lat: 40.8148, lng: -77.8653 });
  const [selectedLocationId, setSelectedLocationId] = useState(null);
  const [routeToId, setRouteToId] = useState(null);
  const navigate = useNavigate();
  
  const [radius, setRadius] = useState(25);
  const [locations, setLocations] = useState(null);

  // Form state for person_filters
  const [formData, setFormData] = useState({
    needs_housing: true,
    beds_needed: 1,
    needs_handicapped_access: false,
    owns_pets: false,
    preferred_duration_days: 30,
    days_homeless: null,
    prefers_family_rooming: false,
    can_pay_fees: false,
    max_affordable_fee: 0,
    lgbtq_identity: false,
    prefers_medical_support: false,
    prefers_counseling: false,
    prefers_meals_provided: false,
    prefers_showers: false,
    duration_flexibility: 'flexible',
    urgency_level: 'within_week',
    max_travel_distance_miles: 25,
    gender: 'other',
    age: 25,
    language: 'english',
    immigration_status: null,
    veteran_status: 'no',
    criminal_record: 'no',
    sobriety: 'no',
    has_id: true,
    needs_food: false,
    needs_clothing: false,
    needs_medical: false,
    needs_mental_health: false
  });

  const handleSelectLocation = useCallback((id) => {
    setSelectedLocationId(id);
    setRouteToId(id);
  }, []);

  const handleClearRoute = () => {
    setSelectedLocationId(null);
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
  }, []);

  const fetchMatches = async () => {
    if (!userLocation) {
      console.log("No user location available yet");
      return;
    }

    // Create a copy of formData for person_filters
    const personFiltersPayload = {
      ...formData,
      max_travel_distance_miles: radius
    };

    // Remove empty optional fields
    if (!personFiltersPayload.days_homeless) delete personFiltersPayload.days_homeless;
    if (!personFiltersPayload.immigration_status) delete personFiltersPayload.immigration_status;

    try {
      console.log("Fetching matches...");
      // Structure the request to match Pydantic model
      const results = await getPeopleMatches({
        location: userLocation,
        radius: radius,
        person_filters: personFiltersPayload
      });
      setLocations(results);
      console.log("Matches loaded successfully!");
    } catch (err) {
      console.error("Error fetching matches:", err);
      setLocations(null);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? Number(value) : value
    }));
  };

  const selectedLocation =
    selectedLocationId && locations
      ? locations[selectedLocationId]
      : null;

  return (
    <div className="main-container">
      <aside className="sidebar">
        <div className="sidebar-top" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <h4 className="mb-3">What are you looking for?</h4>
          
          <div className="survey-form" style={{ flex: 1, overflowY: 'auto', padding: '0 1rem', marginBottom: '1rem' }}>
            {/* Primary Need */}
            <div className="form-section mb-3">
              <label className="form-label fw-bold">I need:</label>
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="radio"
                  name="needs_housing"
                  checked={formData.needs_housing === true}
                  onChange={() => setFormData(prev => ({ ...prev, needs_housing: true }))}
                />
                <label className="form-check-label">Housing/Shelter</label>
              </div>
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="radio"
                  name="needs_housing"
                  checked={formData.needs_housing === false}
                  onChange={() => setFormData(prev => ({ ...prev, needs_housing: false }))}
                />
                <label className="form-check-label">Resources (Food, Clothing, etc.)</label>
              </div>
            </div>

            {/* Housing-specific fields */}
            {formData.needs_housing && (
              <>
                <div className="form-section mb-3">
                  <label className="form-label">Beds Needed</label>
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    name="beds_needed"
                    value={formData.beds_needed}
                    onChange={handleInputChange}
                    min="1"
                  />
                </div>

                <div className="form-section mb-3">
                  <label className="form-label">Preferred Stay Duration (days)</label>
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    name="preferred_duration_days"
                    value={formData.preferred_duration_days}
                    onChange={handleInputChange}
                    min="1"
                  />
                </div>

                <div className="form-section mb-3">
                  <label className="form-label">Days Homeless (optional)</label>
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    name="days_homeless"
                    value={formData.days_homeless}
                    onChange={handleInputChange}
                    min="0"
                    placeholder="Optional"
                  />
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="needs_handicapped_access"
                    checked={formData.needs_handicapped_access}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Need Handicapped Access</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="owns_pets"
                    checked={formData.owns_pets}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Have Pets</label>
                </div>

                <hr className="my-3" />
                <h6 className="fw-bold mb-2">Preferences (Optional)</h6>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="prefers_family_rooming"
                    checked={formData.prefers_family_rooming}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Prefer Family Rooming</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="prefers_medical_support"
                    checked={formData.prefers_medical_support}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Prefer Medical Support</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="prefers_counseling"
                    checked={formData.prefers_counseling}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Prefer Counseling</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="prefers_meals_provided"
                    checked={formData.prefers_meals_provided}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Prefer Meals Provided</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="prefers_showers"
                    checked={formData.prefers_showers}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Prefer Showers</label>
                </div>

                <div className="form-section mb-3">
                  <label className="form-label">Can Pay Fees?</label>
                  <select className="form-select form-select-sm" name="can_pay_fees" value={formData.can_pay_fees} onChange={e => setFormData(prev => ({ ...prev, can_pay_fees: e.target.value === 'true' }))}>
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                  </select>
                </div>

                {formData.can_pay_fees && (
                  <div className="form-section mb-3">
                    <label className="form-label">Max Affordable Fee ($)</label>
                    <input
                      type="number"
                      className="form-control form-control-sm"
                      name="max_affordable_fee"
                      value={formData.max_affordable_fee}
                      onChange={handleInputChange}
                      min="0"
                    />
                  </div>
                )}
              </>
            )}

            {/* Resource needs (for charity matching) */}
            {!formData.needs_housing && (
              <>
                <h6 className="fw-bold mb-2">What do you need?</h6>
                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="needs_food"
                    checked={formData.needs_food}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Food</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="needs_clothing"
                    checked={formData.needs_clothing}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Clothing</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="needs_medical"
                    checked={formData.needs_medical}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Medical Supplies</label>
                </div>

                <div className="form-check mb-2">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    name="needs_mental_health"
                    checked={formData.needs_mental_health}
                    onChange={handleInputChange}
                  />
                  <label className="form-check-label">Mental Health Support</label>
                </div>
              </>
            )}

            <hr className="my-3" />
            <h6 className="fw-bold mb-2">Personal Information</h6>

            <div className="form-section mb-3">
              <label className="form-label">Urgency</label>
              <select className="form-select form-select-sm" name="urgency_level" value={formData.urgency_level} onChange={handleInputChange}>
                <option value="immediate">Immediate</option>
                <option value="within_week">Within a Week</option>
                <option value="within_month">Within a Month</option>
              </select>
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Gender</label>
              <select className="form-select form-select-sm" name="gender" value={formData.gender} onChange={handleInputChange}>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other/Prefer not to say</option>
              </select>
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Age</label>
              <input
                type="number"
                className="form-control form-control-sm"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                min="18"
                max="100"
              />
            </div>

            <div className="form-check mb-2">
              <input
                className="form-check-input"
                type="checkbox"
                name="lgbtq_identity"
                checked={formData.lgbtq_identity}
                onChange={handleInputChange}
              />
              <label className="form-check-label">LGBTQ+ Identity</label>
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Language</label>
              <input
                type="text"
                className="form-control form-control-sm"
                name="language"
                value={formData.language}
                onChange={handleInputChange}
                placeholder="e.g., english, spanish"
              />
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Veteran?</label>
              <select className="form-select form-select-sm" name="veteran_status" value={formData.veteran_status} onChange={handleInputChange}>
                <option value="no">No</option>
                <option value="yes">Yes</option>
              </select>
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Immigration Status (optional)</label>
              <select className="form-select form-select-sm" name="immigration_status" value={formData.immigration_status} onChange={handleInputChange}>
                <option value="">Prefer not to say</option>
                <option value="citizen">Citizen</option>
                <option value="permanent_resident">Permanent Resident</option>
                <option value="temporary_resident">Temporary Resident</option>
                <option value="refugee">Refugee</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Criminal Record?</label>
              <select className="form-select form-select-sm" name="criminal_record" value={formData.criminal_record} onChange={handleInputChange}>
                <option value="no">No</option>
                <option value="yes">Yes</option>
              </select>
            </div>

            <div className="form-section mb-3">
              <label className="form-label">Currently Sober?</label>
              <select className="form-select form-select-sm" name="sobriety" value={formData.sobriety} onChange={handleInputChange}>
                <option value="no">No</option>
                <option value="yes">Yes</option>
              </select>
            </div>
          </div>

          <div style={{ padding: '0 1rem', paddingBottom: '1rem' }}>
            <button
              className="btn btn-primary add-item-button"
              style={{ width: '100%', padding: '1rem' }}
              onClick={fetchMatches}
            >
              Filter
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <div className="main-content-wrapper">
          <div className="map-wrapper">
            <div className="map-container">
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

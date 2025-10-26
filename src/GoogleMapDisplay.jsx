import React, { useEffect, useRef } from 'react';

const GoogleMapDisplay = () => {
  // 1. Get the API Key
  const API_KEY = process.env.REACT_APP_GOOGLE_MAP_API_KEY;
  console.log('Loading map with key:', API_KEY);

  // 2. Create a ref to hold the map's DOM element
  const mapRef = useRef(null);
  // Get and display locations


  //example locations 
  const locations = [{
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
  }]



  for (const ID in locations) {
    // Check if the property is actually an own property of the object
    if (locations.hasOwnProperty(ID)) {
        const data = locations[ID];

        // Create a new marker for the current location
        const marker = new google.maps.Marker({
            position: data.location,
            map: map,
            title: data.name // Use the dictionary key as the marker title
        });

        // Optional: Add an Info Window (a common feature for POIs)
        const infoWindow = new google.maps.InfoWindow({
            content: `<h3>${data.name}</h3>
            <p>Hours: ${data.hours}</p>
            <hr>
            <p>${data.description}</p>`
        });

        marker.addListener("click", () => {
            infoWindow.open({
                anchor: marker,
                map
            });
        });
    }

  // 3. Effect to load the script and initialize the map
  useEffect(() => {
    // Define the map initialization function
    const initMap = () => {
      // Coordinates for the center of the map (e.g., San Francisco)
      const center = { lat: 40.8148, lng: -77.8653 };

      // Initialize the map on the referenced DOM element
      new window.google.maps.Map(mapRef.current, {
        center: center,
        zoom: 13, // Default zoom level
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
        mapId: "DEMO_MAP_ID",

        styles: [
          {
            featureType: "poi",
            stylers: [{ visibility: "off" }],
          },
        ],
      });
    };

    // Check if the Google Maps script is already loaded
    if (!window.google) {
      // Create the script element
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&callback=initMap&v=weekly&libraries=marker`;
      script.async = true;

      // Attach the initialization function to the window global object
      window.initMap = initMap;

      // Append the script to the document head
      document.head.appendChild(script);

      return () => {
        // Cleanup function (optional, but good practice)
        delete window.initMap;
        // Note: Removing the script itself is more complex and often skipped
      };
    } else {
      // If the script is already loaded, just initialize the map
      initMap();
    }
  }, [API_KEY]); // Rerun effect if API_KEY changes (unlikely)

  // 4. Render a div that will serve as the map container
  return (
    <div
      ref={mapRef}
      style={{ width: '100%', height: '400px' }} // MUST define dimensions
      aria-label="Google Map"
    >
      {/* Map will be rendered inside this div */}
    </div>
  );
};
}
export default GoogleMapDisplay;
import React, { useEffect, useRef } from 'react';

const GoogleMapDisplay = () => {
  // 1. Get the API Key
  const API_KEY = process.env.REACT_APP_GOOGLE_MAP_API_KEY;
  console.log('Loading map with key:', API_KEY);

  // 2. Create a ref to hold the map's DOM element
  const mapRef = useRef(null);

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
      script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&callback=initMap&v=weekly`;
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

export default GoogleMapDisplay;
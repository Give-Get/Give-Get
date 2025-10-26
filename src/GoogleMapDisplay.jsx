import React, { useEffect, useRef } from 'react';

const GoogleMapDisplay = () => {
  const API_KEY = process.env.REACT_APP_GOOGLE_MAP_API_KEY;
  const mapRef = useRef(null);
  
  // FIX D: Remove the array wrapper [] to make 'locations' a proper dictionary object.
  const locations = {
    "4": {
      "type": {"shelter": true, "charity": false},
      "EIN": 6,
      "name": "Shelter1",
      "address": "123 Shelter St",
      "location": { "lat": 0, "lng": 0},
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
      // ... rest of location 4 data
    },
    "1": {
      "type": {"shelter": false, "charity": true},
      "EIN": 0,
      "name": "Centre County Food Bank",
      "address": "123 Main St, State College, PA",
      "location": { "lat": 40.793, "lng": -77.86 },
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
      // ... rest of location 1 data
    }
  }; // Changed from [{...}] to {...}

  // 1. Map Initialization and Marker Creation Effect
  // FIX B & C: All map logic and marker creation MUST be inside the effect.
  useEffect(() => {
    // Variable to hold the map instance after creation
    let mapInstance;

    // Define the map initialization function
    const initMap = () => {
      const center = { lat: 40.8148, lng: -77.8653 };

      // Initialize the map and store the instance
      mapInstance = new window.google.maps.Map(mapRef.current, {
        center: center,
        zoom: 13,
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
      
      // Call the function to add markers once the map is ready
      addMarkers(mapInstance, locations);
    }; // End of initMap function

    // ... (Script loading logic is correct, assuming API_KEY is loaded)
    
    if (!window.google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&callback=initMap&v=weekly&libraries=marker`;
      script.async = true;

      window.initMap = initMap;
      document.head.appendChild(script);

      return () => {
        delete window.initMap;
      };
    } else {
      initMap();
    }
  }, [API_KEY, locations]); // End of useEffect

  // 2. Separate Marker Creation Function
  // This function is now outside the loop and accepts the map instance.
  const addMarkers = (map, locationsData) => {
    // FIX C: 'map' is now correctly passed as an argument.
    /* global google */ // Recommended for the linter

    for (const ID in locationsData) {
        if (locationsData.hasOwnProperty(ID)) {
            const data = locationsData[ID];

            // FIX B: Marker creation is now correctly nested in a standard function call.
            const marker = new google.maps.Marker({ // Using Advanced Marker to resolve deprecation
                map: map,
                position: data.location,
                title: data.name
            });

            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <h3>${data.name}</h3>
                    <p>Hours: ${data.hours.monday} - ${data.hours.sunday}</p>
                    <hr>
                    <p>${data.description}</p>
                `
            });

            marker.addListener("click", () => {
                infoWindow.open({
                    anchor: marker,
                    map
                });
            });
        }
    }
  }


  // 3. Render the Map Container
  // FIX A: Return statement is now correctly placed outside of the hook.
  return (
    <div
      ref={mapRef}
      style={{ width: '100%', height: '400px' }}
      aria-label="Google Map"
    />
  );
};
// FIX A: Export is now correctly placed outside the function block.
export default GoogleMapDisplay;
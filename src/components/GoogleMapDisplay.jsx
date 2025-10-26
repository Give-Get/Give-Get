import React, { useEffect, useRef, useCallback } from 'react';
import '../App.css';

// --- 1. MODIFICATION: Accept selectedLocationId as a prop ---
const GoogleMapDisplay = ({ selectedLocationId, routeToId, locations, userLocation, onMarkerClick, onInfoClose}) => {
  const API_KEY = process.env.REACT_APP_GOOGLE_MAP_API_KEY;
  const mapRef = useRef(null); // Ref for the map container <div>
  
  const mapInstanceRef = useRef(null);
  const directionsServiceRef = useRef(null);
  const directionsRendererRef = useRef(null);

  // --- 2. MODIFICATION: Add refs for markers and info windows ---
  const markersRef = useRef({});
  const infoWindowsRef = useRef({});

  // --- NEW: 1. Create refs to store the latest callback props ---
  // This allows us to remove them from effect dependencies, preventing
  // re-initialization when the parent component re-renders.
  const onMarkerClickRef = useRef(onMarkerClick);
  onMarkerClickRef.current = onMarkerClick; // Update on every render

  const onInfoCloseRef = useRef(onInfoClose);
  onInfoCloseRef.current = onInfoClose; // Update on every render

  // 2. Function to calculate and display route (Already correctly memoized)
  const calculateAndDisplayRoute = useCallback((destination) => {
    if (!userLocation) {
      alert("Could not get your location. Please ensure location services are enabled.");
      return;
    }

    if (!directionsServiceRef.current || !directionsRendererRef.current) {
      console.error("Directions services are not initialized.");
      return;
    }
    
    // Clear any previous route
    directionsRendererRef.current.setDirections({ routes: [] });

    const request = {
      origin: userLocation,
      destination: destination,
      travelMode: 'DRIVING',
    };

    directionsServiceRef.current.route(request, (result, status) => {
      if (status === 'OK') {
        directionsRendererRef.current.setDirections(result);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
  }, [userLocation]); // Depends only on userLocation

  // --- NEW: 2. Wrap addMarkers in useCallback ---
  // By using an empty dependency array [], this function is created only ONCE.
  // It uses the refs (onMarkerClickRef, onInfoCloseRef) to access the
  // *latest* prop functions without needing them as dependencies.
  const addMarkers = useCallback((map, locationsData) => {
    /* global google */ 

    // --- NEW: Clear old markers before adding new ones ---
    // This is crucial if this effect re-runs (e.g., if `locations` changes).
    Object.values(markersRef.current).forEach(marker => {
      google.maps.event.clearInstanceListeners(marker);
      marker.setMap(null);
    });
    Object.values(infoWindowsRef.current).forEach(infoWindow => {
      google.maps.event.clearInstanceListeners(infoWindow);
    });
    markersRef.current = {};
    infoWindowsRef.current = {};
    // --- End of new clearing logic ---

    for (const ID in locationsData) {
        if (locationsData.hasOwnProperty(ID)) {
            const data = locationsData[ID];
            const marker = new google.maps.Marker({
                map: map,
                position: data.location,
                title: data.name
            });

            // --- Modification: Simplified InfoWindow content ---
            const infoWindowContent = `
                <div style="font-family: Arial, sans-serif; max-width: 250px;">
                    <h3 style="margin: 0 0 10px;">${data.name}</h3>
                    <hr style="border: 0; border-top: 2px solid #000000;">
                    <h6 style="margin: 0 0 10px;">Address:</h6>
                    <p style="margin: 5px 0;">${data.address}</p>
                    <hr style="border: 0; border-top: 2px solid #000000;">
                    <h6 style="margin: 0 0 10px;">Hours:</h6>
                    <p style="margin: 5px 0;">Monday: ${data.hours.monday}<br>Tuesday: ${data.hours.tuesday}<br>Wednesdday: ${data.hours.wednesday}<br>Thursday: ${data.hours.thursday}<br>Friday:${data.hours.friday}<br>Saturday:${data.hours.saturday}<br>Sunday:${data.hours.sunday}<br></p>
                    <hr style="border: 0; border-top: 2px solid #000000;">
                    <h6 style="margin: 0 0 10px;">Description:</h6>
                    <p style="margin: 5px 0;">${data.description}</p>
                </div>
            `;
            const infoWindow = new google.maps.InfoWindow({ content: infoWindowContent });

            // --- 6. MODIFICATION: Store instances in refs ---
            markersRef.current[ID] = marker;
            infoWindowsRef.current[ID] = infoWindow;

            marker.addListener("click", () => {
              // --- 7. MODIFICATION: Removed infoWindow.open() ---
              
              // --- NEW: 3. Call the callback from the ref ---
              if (onMarkerClickRef.current) {
                onMarkerClickRef.current(ID);
              }
            });

            infoWindow.addListener('closeclick', () => {
              // --- NEW: 4. Call the callback from the ref ---
              if (onInfoCloseRef.current){
                onInfoCloseRef.current()
              }
            });
        }
    }
  }, []); // <-- Empty dependency array makes this function stable

  // 3. Map Initialization Effect
  useEffect(() => {
    const initMap = () => {
      const center = userLocation || { lat: 40.7128, lng: -74.0060 }; // Fallback center

      mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
        center: center,
        zoom: 13,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
        styles: [ {
          "featureType": "poi",
          "stylers": [
            {
              "visibility": "off"
            } ],
          }]
      });
      
      directionsServiceRef.current = new window.google.maps.DirectionsService();
      directionsRendererRef.current = new window.google.maps.DirectionsRenderer();
      directionsRendererRef.current.setMap(mapInstanceRef.current);

      // --- 3. MODIFICATION: Pass all dependencies to addMarkers ---
      addMarkers(mapInstanceRef.current, locations);
    };

    if (!window.google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&callback=initMap&v=weekly&libraries=marker,routes`;
      script.async = true;

      window.initMap = initMap;
      document.head.appendChild(script);

      return () => {
        delete window.initMap;
      };
    } else {
      // --- NEW: Only re-initialize if `locations` changed ---
      // This is a basic check. If the map instance exists, we
      // just want to re-add the markers, not re-create the map.
      if (!mapInstanceRef.current) {
        initMap();
      } else {
        // If map already exists, just update markers
        addMarkers(mapInstanceRef.current, locations);
      }
    }
  // --- NEW: 5. Update dependency array ---
  // We remove onMarkerClick/onInfoClose and add the stable `addMarkers`.
  // The map will still re-run this logic if `locations` changes,
  // but *not* if the callback props change.
  }, [API_KEY, locations, addMarkers, userLocation]); 


  // --- 8. MODIFICATION: Add Effect to watch for selectedLocationId prop changes ---
  // (This was already correct and did not reload the map)
  useEffect(() => {
    const map = mapInstanceRef.current;
    const allInfoWindows = infoWindowsRef.current;
    const allMarkers = markersRef.current;

    if (!map) return; // Map not ready

    // 1. Close all other info windows
    Object.values(allInfoWindows).forEach(infoWindow => infoWindow.close());

    // 2. If a new location is selected, open its window
    if (selectedLocationId) {
      const infoWindow = allInfoWindows[selectedLocationId];
      const marker = allMarkers[selectedLocationId];

      if (infoWindow && marker) {
        infoWindow.open({ anchor: marker, map });
      }
    }
  }, [selectedLocationId]); // Dependency: This code re-runs ONLY when selectedLocationId changes


  // --- Addition: 5. Effect to watch for routeToId prop changes ---
  // (This was also correct)
  useEffect(() => {
    // Check if we have an ID, the map is ready, and the location exists
    if (routeToId && mapInstanceRef.current && directionsServiceRef.current && locations[routeToId]) {
      const destination = locations[routeToId].location;
      if (destination) {
        calculateAndDisplayRoute(destination);
      }
    }
    
    // If routeToId is cleared (e.g., set to null), clear the displayed route
    if (!routeToId && directionsRendererRef.current) {
         directionsRendererRef.current.setDirections({ routes: [] });
    }
    
  }, [routeToId, locations, calculateAndDisplayRoute]); // Reruns when routeToId changes


  // 6. Render the Map Container
  return (
    <div
      ref={mapRef}
      style={{ width: '100%', height: '100%' }}
      aria-label="Google Map"
    />
  );
};

export default GoogleMapDisplay;
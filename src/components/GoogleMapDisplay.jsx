import React, { useEffect, useRef } from 'react';
import '../App.css';

// --- Modification: Accept routeToId as a prop ---
const GoogleMapDisplay = ({ routeToId, locations, userLocation, onMarkerClick, onInfoClose}) => {
  const API_KEY = process.env.REACT_APP_GOOGLE_MAP_API_KEY;
  const mapRef = useRef(null); // Ref for the map container <div>
  
  const mapInstanceRef = useRef(null);
  const directionsServiceRef = useRef(null);
  const directionsRendererRef = useRef(null);

  // 2. Function to calculate and display route
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

  // 3. Map Initialization Effect
  useEffect(() => {
    const initMap = () => {
      const center = userLocation;

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

      addMarkers(mapInstanceRef.current, locations, onMarkerClick);
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
      initMap();
    }
  }, [API_KEY, locations, onMarkerClick]); // This effect only runs once to init the map

  // 4. Marker Creation Function (Simplified)
  // --- Modification: Removed 'onGetDirections' parameter and button logic ---
  const addMarkers = (map, locationsData, onMarkerClick) => {
    /* global google */ 
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
                    <h6 style="margin: 0 0 10px;">Address:</h3>
                    <p style="margin: 5px 0;">${data.address}</p>
                    <hr style="border: 0; border-top: 2px solid #000000;">
                    <h6 style="margin: 0 0 10px;">Hours:</h3>
                    <p style="margin: 5px 0;">Monday: ${data.hours.monday}<br>Tuesday: ${data.hours.tuesday}<br>Wednesdday: ${data.hours.wednesday}<br>Thursday: ${data.hours.thursday}<br>Friday:${data.hours.friday}<br>Saturday:${data.hours.saturday}<br>Sunday:${data.hours.sunday}<br></p>
                    <hr style="border: 0; border-top: 2px solid #000000;">
                    <h6 style="margin: 0 0 10px;">Description:</h3>
                    <p style="margin: 5px 0;">${data.description}</p>
                </div>
            `;
            const infoWindow = new google.maps.InfoWindow({ content: infoWindowContent });
            marker.addListener("click", () => {
              // 1. Keep the existing info window logic
              infoWindow.open({ anchor: marker, map }); 
              
              // 2. Call the function from the parent, passing the ID
              if (onMarkerClick) {
                onMarkerClick(ID);
              }
            });

            infoWindow.addListener('closeclick', () => {
              if (onInfoClose){
                onInfoClose()
              }
            });
        }
    }
  }

  // --- Addition: 5. Effect to watch for routeToId prop changes ---
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
      style={{ width: '100%', height: '400px' }}
      aria-label="Google Map"
    />
  );
};

export default GoogleMapDisplay;
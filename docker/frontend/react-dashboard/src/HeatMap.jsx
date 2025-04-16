import React, { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";

const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];
const API_HOST = process.env.REACT_APP_API_HOST;

const HeatMap = React.memo(({ urlQuery, selectedDisasterType }) => {
  const [map, setMap] = useState(null);
  const [heatLayer, setHeatLayer] = useState(null);
  const [coordinates, setCoordinates] = useState([]);

  // Regular function for fetching coordinates, not a hook
  const fetchCoordinates = async (disasterType = "earthquake", query = "") => {
    const allData = [];

    try {
      let url = `${API_HOST}/fetch-coordinates-by-label?disaster_type=${disasterType}${query ? ("&" + query) : ""}`;

      const response = await fetch(url);
      if (!response.ok) {
        console.warn(`Failed to fetch for ${disasterType}`);
        return [];
      }

      const text = await response.text(); // Get the response as text
      
      // Check if the response contains invalid values like "NaN"
      if (text.includes("NaN") || text.trim() === "") {
        console.error(`Invalid response content for ${disasterType}:`, text);
        return [];
      }

      console.log(`Raw response for ${disasterType}:`, text); // Log raw response for debugging

      let data = [];
      try {
        data = JSON.parse(text); // Try parsing the JSON
      } catch (e) {
        console.error(`Invalid JSON response for ${disasterType}:`, e);
        return [];
      }

      // Ensure the data is an array and contains valid coordinates
      if (!Array.isArray(data)) {
        console.error(`Invalid data structure for ${disasterType}:`, data);
        return [];
      }

      // Filter out any coordinates with NaN values in lat or lng
      const validCoordinates = data.filter((coord, index) => {
        const isValidLat = !isNaN(coord.lat) && coord.lat !== null && coord.lat !== undefined;
        const isValidLng = !isNaN(coord.lng) && coord.lng !== null && coord.lng !== undefined;

        // Log invalid coordinates for debugging
        if (!isValidLat || !isValidLng) {
          console.warn(`Invalid coordinates at index ${index} for ${disasterType}:`, coord);
        }

        return isValidLat && isValidLng;
      });

      // Log the valid coordinates after filtering
      console.log(`Valid coordinates for ${disasterType}:`, validCoordinates);

      allData.push(...validCoordinates);
    } catch (error) {
      console.error(`Error fetching ${disasterType}:`, error);
    }

    return allData;
  };
  
  // Normalize sentiment from [-1, 1] → [0, 1]
  const normalizeSentiment = (value) => (value + 1) / 2;
  
  useEffect(() => {
    if (!map) {
      const newMap = L.map("heatmap", {
        center: [37.8, -96], // Center of the US
        zoom: 5,
        minZoom: 1,
        maxZoom: 10,
        maxBounds: [
          [-90, -180], // Southwest
          [90, 180],   // Northeast
        ],
        maxBoundsViscosity: 0.5,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(newMap);
      setMap(newMap);
    }
  }, [map]);

  useEffect(() => {
    console.log("HeatMap updated:", selectedDisasterType);
    
    // Use an async function inside useEffect to fetch data
    const getCoordinates = async () => {
      const data = await fetchCoordinates(selectedDisasterType, urlQuery);
      console.log("Coordinates for heatmap:", data);
      setCoordinates(data);
    };
    
    getCoordinates();
  }, [urlQuery, selectedDisasterType]);

  useEffect(() => {
    if (map && coordinates.length > 0) {
      // Remove the previous heatmap layer if it exists
      if (heatLayer) {
        map.removeLayer(heatLayer);
      }

      // Normalize sentiment from [-1, 1] → [0, 1]
      const points = coordinates.map((coord) => {
        const normalizedIntensity = normalizeSentiment(coord.sentiment_scaled);
        return [coord.lat, coord.lng, normalizedIntensity];
      });

      console.log("POINTS: ", points);

      const style = getComputedStyle(document.documentElement)
      
      // Create the heatmap layer with the new data
      const newHeatLayer = L.heatLayer(points, {
        radius: 20,
        blur: 5,
        maxZoom: 4,
        gradient: {
          0.0: style.getPropertyValue('--purple'), // Purple — high sentiment (low intensity)
          0.25: style.getPropertyValue('--green'), // Green — medium sentiment (low intensity)
          0.5: style.getPropertyValue('--yellow'),  // Yellow — neutral
          0.75: style.getPropertyValue('--orange'), // Orange — low sentiment (medium intensity)
          1.0: style.getPropertyValue('--red')   // Red — low sentiment (high intensity)
        }
        
      }).addTo(map);
      setHeatLayer(newHeatLayer); // Update the state to keep track of the heatLayer
    }
  }, [map, coordinates, heatLayer]);

  return (
    <div id="heatmap" className="mt-3" style={{ height: "250px", background: "lightgray" }}></div>
  );
});

export default HeatMap;

import React, { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";
import useFetchCoordinates from "./useFetchCoordinates";

const HeatMap = React.memo(({ urlQuery, selectedDisasterType }) => {
  const [map, setMap] = useState(null);
  const [heatLayer, setHeatLayer] = useState(null);
  const coordinates = useFetchCoordinates(selectedDisasterType, urlQuery);
  
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

    console.log("HeatMap updated:", selectedDisasterType);
    console.log("Coordinates for heatmap:", coordinates);

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
      
      // Create the heatmap layer with the new data
      const newHeatLayer = L.heatLayer(points, {
        radius: 20,
        blur: 5,
        maxZoom: 4,
        gradient: {
          0.0: "#00ff00", // Green — high sentiment (low intensity)
          0.25: "#aaff00", 
          0.5: "#ffff00",  // Yellow — neutral
          0.75: "#ffaa00",
          1.0: "#ff0000"   // Red — low sentiment (high intensity)
        }
        
      }).addTo(map);

      setHeatLayer(newHeatLayer); // Update the state to keep track of the heatLayer
    }
  }, [map, coordinates, urlQuery, selectedDisasterType]);  // Trigger this effect when selectedDisasterType or coordinates change

  return (
    <div id="heatmap" className="mt-3" style={{ height: "250px", background: "lightgray" }}></div>
  );
});

export default HeatMap;

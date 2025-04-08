import React, { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";
import useFetchCoordinates from "./useFetchCoordinates"; // Import the custom hook

const HeatMap = () => {
  const [map, setMap] = useState(null);
  const [heatLayer, setHeatLayer] = useState(null);
  const coordinates = useFetchCoordinates(); // Fetch coordinates

  useEffect(() => {
    // Initialize the map only once
    if (!map) {
      if (L.DomUtil.get("heatmap") !== null) {
        L.DomUtil.get("heatmap")._leaflet_id = null;
      }

      const newMap = L.map("heatmap", {
        center: [37.8, -96], // Center of the US
        zoom: 5,
        minZoom: 3,
        maxZoom: 11,
        maxBounds: [
          [15, -175], // Southwest corner
          [55, -70], // Northeast corner
        ],
        maxBoundsViscosity: 0.5, // Keeps the map inside bounds
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(newMap);
      setMap(newMap);
    }
  }, [map]);

  useEffect(() => {
    if (map && coordinates.length > 0) {
      if (heatLayer) {
        map.removeLayer(heatLayer);
      }

      // Filter points within the US
      const usCoordinates = coordinates.filter(
        (coord) =>
          coord.latitude >= 15 && coord.latitude <= 55 && // Latitude range
          coord.longitude >= -175 && coord.longitude <= -70 // Longitude range
      );

      const heatPoints = usCoordinates.map(coord => [coord.latitude, coord.longitude, 1.0]);
      const newHeatLayer = L.heatLayer(heatPoints, { radius: 25, blur: 15, maxZoom: 10 }).addTo(map);
      setHeatLayer(newHeatLayer);
    }
  }, [map, coordinates]); // Only update when coordinates change

  return (
    <div id="heatmap" style={{ height: "250px", background: "lightgray" }}></div>
  );
};

export default HeatMap;
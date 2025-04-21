import React, { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";
import useFetchCoordinates from "./useFetchCoordinates";

const HeatMap = React.memo(({ urlQuery, selectedDisasterType }) => {
  const coordinates = useFetchCoordinates(selectedDisasterType, urlQuery); // ✅ always fetches based on prop
  const [mapInstance, setMapInstance] = useState(null);
  const [heatLayer, setHeatLayer] = useState(null);

  useEffect(() => {
    if (!mapInstance) {
      const map = L.map("heatmap", {
        center: [37.8, -96],
        zoom: 5,
        minZoom: 1,
        maxZoom: 11,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 0.5,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);
      setMapInstance(map);
    }
  }, [mapInstance]);

  useEffect(() => {
    if (!mapInstance || coordinates.length === 0) return;

    if (heatLayer) {
      mapInstance.removeLayer(heatLayer);
    }

    const normalize = (value) => Math.min(Math.max(value, 0), 1);

    const points = coordinates.map((coord) => {
      const rawIntensity = 1 - coord.sentiment;
      return [coord.lat, coord.lng, normalize(rawIntensity)];
    });
    const style = getComputedStyle(document.documentElement);
    const newHeatLayer = L.heatLayer(points, {
      radius: 20,
      blur: 10,
      maxZoom: 4,
      gradient: {
        0.0: style.getPropertyValue('--purple'), // Purple — high sentiment (low intensity)
        0.25: style.getPropertyValue('--green'), // Green — medium sentiment (low intensity)
        0.5: style.getPropertyValue('--yellow'),  // Yellow — neutral
        0.75: style.getPropertyValue('--orange'), // Orange — low sentiment (medium intensity)
        1.0: style.getPropertyValue('--red')   // Red — low sentiment (high intensity)
      },
    }).addTo(mapInstance);

    setHeatLayer(newHeatLayer);

    console.log("🟢 Heatmap updated with:", selectedDisasterType);
    console.log("🟡 Plotted coordinates:", coordinates);
  }, [mapInstance, coordinates, selectedDisasterType]); // 🔁 react to disasterType properly

  return <div id="heatmap" className="mt-3" style={{ height: "250px", background: "lightgray" }}></div>;
});

export default HeatMap;

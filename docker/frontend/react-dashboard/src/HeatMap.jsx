import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet.heat";
import useFetchCoordinates from "./useFetchCoordinates"; // Import the custom hook

const HeatMap = () => {
    const [map, setMap] = useState(null);
    const [heatLayer, setHeatLayer] = useState(null);
    const coordinates = useFetchCoordinates(); // Use the hook

    useEffect(() => {
        if (!map) {
            if (L.DomUtil.get("heatmap") !== null) {
                L.DomUtil.get("heatmap")._leaflet_id = null;
            }

            const newMap = L.map("heatmap").setView([37.7749, -122.4194], 5);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(newMap);
            setMap(newMap);
        }

        if (map && coordinates.length > 0) {
            if (heatLayer) {
                map.removeLayer(heatLayer);
            }
            const heatPoints = coordinates.map((coord) => [coord.latitude, coord.longitude, 1.0]);
            const newHeatLayer = L.heatLayer(heatPoints, { radius: 25, blur: 15, maxZoom: 10 }).addTo(map);
            setHeatLayer(newHeatLayer);
        }
    }, [map, coordinates]);

    return (
        <Card className="shadow-sm" style={{ height: "400px", margin: "auto" }}>
            <Card.Body>
                <Card.Title>Heat Map</Card.Title>
                <div id="heatmap" style={{ height: "350px", background: "lightgray" }}></div>
            </Card.Body>
        </Card>
    );
};

export default HeatMap;

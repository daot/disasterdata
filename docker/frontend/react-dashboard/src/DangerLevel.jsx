import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";

const API_HOST = "https://api.disasterdata.duckdns.org";

const DangerLevel = () => {
    const [dangerLevel, setDangerLevel] = useState({ label: "None", color: "#50fa7b", disasterType: "", location: "" });

    useEffect(() => {
        const fetchDangerLevel = async () => {
            try {
                //const response = await fetch('/fetch-top-disaster-last-day');  // Make sure this route is correct
                const response = await fetch(API_HOST + '/fetch-top-disaster-last-day'); 
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const data = await response.json();

                if (data.Error) {
                    console.warn("No valid disaster data found.");
                    return;
                }

                let color = "#50fa7b"; // Default green for 'None'
                if (data.danger_level === "high") color = "red";
                else if (data.danger_level === "moderate") color = "orange";
                else if (data.danger_level === "low") color = "gold";

                setDangerLevel({
                    label: data.danger_level.charAt(0).toUpperCase() + data.danger_level.slice(1),
                    color,
                    disasterType: data.top_label,
                    location: data.location
                });

            } catch (error) {
                console.error("Error fetching danger level:", error);
            }
        };

        fetchDangerLevel();

        const intervalId = setInterval(fetchDangerLevel, 60000);

        return () => clearInterval(intervalId);
    }, []);

    return (
        <Card className="shadow-sm" style={{ height: "100px", border: `2px solid ${dangerLevel.color}` }}>
            <Card.Body>
                <Card.Title style={{ fontSize: "0.75rem" }}>Danger Level</Card.Title>
                <p style={{ fontSize: "1.25rem", fontWeight: "bold", color: dangerLevel.color }}>
                    {dangerLevel.label}
                </p>
            </Card.Body>
        </Card>
    );
};

export default DangerLevel;

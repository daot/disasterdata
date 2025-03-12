import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";

const API_HOST = "https://api.disasterdata.duckdns.org";

const DangerLevel = () => {
    const [dangerLevel, setDangerLevel] = useState({ label: "None", color: "green" });

    const fetchPostsOverTime = async () => {
        const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "blizzard"];
        let totalPostCount = 0;

        for (const type of disasterTypes) {
            try {
                const response = await fetch(`${API_HOST}/fetch-posts-over-time/?label=${type}`);
                //const response = await fetch(`/fetch-posts-over-time/?label=${type}`);
                const data = await response.json();

                // Sum up post counts
                totalPostCount += data.reduce((sum, item) => sum + item.count, 0);
            } catch (error) {
                console.error(`Error fetching posts for ${type}:`, error);
            }
        }

        // Determine danger level
        let newDangerLevel = { label: "None", color: "green" };

        if (totalPostCount > 1000) {
            newDangerLevel = { label: "High", color: "red" };
        } else if (totalPostCount > 500) {
            newDangerLevel = { label: "Medium", color: "orange" };
        } else if (totalPostCount > 100) {
            newDangerLevel = { label: "Low", color: "yellow" };
        }

        setDangerLevel(newDangerLevel);
    };

    useEffect(() => {
        fetchPostsOverTime();
    }, []);

    return (
        <Card className="shadow-sm" style={{ height: "100px", border: `2px solid ${dangerLevel.color}` }}>
            <Card.Body>
                <Card.Title style={{ fontSize: "1rem" }}>Danger Level</Card.Title>
                <p style={{ fontSize: "1.25rem", fontWeight: "bold", color: dangerLevel.color }}>
                    {dangerLevel.label}
                </p>
            </Card.Body>
        </Card>
    );
};

export default DangerLevel;

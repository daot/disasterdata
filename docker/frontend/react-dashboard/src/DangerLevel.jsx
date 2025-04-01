import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";

//const API_HOST = "https://api.disasterdata.duckdns.org";

const DangerLevel = () => {
    const [dangerLevel, setDangerLevel] = useState({ label: "None", color: "green", disasterType: "" });

    const fetchPostsOverTime = async () => {
        const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "blizzard"];
        let maxPostCount = 0;
        let mostFrequentDisaster = "None";
    
        for (const type of disasterTypes) {
            try {
                const response = await fetch(`/fetch-posts-over-time/?disaster_type=${type}`);
                //const response = await fetch(API_HOST + `/fetch-posts-over-time/?disaster_type=${type}`);
    
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
    
                const data = await response.json();
    
                // Filter data from the last 24 hours
                const filteredData = data.filter(item => {
                    const itemDate = new Date(item.timestamp);
                    const now = new Date();
                    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
                    return itemDate >= oneDayAgo && itemDate <= now;
                });
    
                const typePostCount = filteredData.reduce((sum, item) => sum + (item.post_count || 0), 0);
    
                if (typePostCount > maxPostCount) {
                    maxPostCount = typePostCount;
                    mostFrequentDisaster = type;
                }
            } catch (error) {
                console.error(`Error fetching posts for ${type}:`, error);
            }
        }

        console.log(`Final Most Frequent Disaster: ${mostFrequentDisaster}, Post Count: ${maxPostCount}`);
    
        // Determine danger level based on max post count of a single disaster type
        let newDangerLevel = { label: "None", color: "#50fa7b", disasterType: mostFrequentDisaster };
    
        if (maxPostCount > 5000) {
            newDangerLevel = { label: "High", color: "red", disasterType: mostFrequentDisaster };
        } else if (maxPostCount > 3000) {
            newDangerLevel = { label: "Medium", color: "orange", disasterType: mostFrequentDisaster };
        } else if (maxPostCount > 1000) {
            newDangerLevel = { label: "Low", color: "gold", disasterType: mostFrequentDisaster };
        }
    
        setDangerLevel(newDangerLevel);
    };
    
    useEffect(() => {
        fetchPostsOverTime();
    }, []);

    return (
        <Card className="shadow-sm" style={{ height: "100px", border: `2px solid ${dangerLevel.color}` }}>
            <Card.Body>
                <Card.Title style={{ fontSize: "0.75rem" }}>Danger Level</Card.Title>
                <p style={{ fontSize: "1.25rem", fontWeight: "bold", color: dangerLevel.color }}>
                    {dangerLevel.label} {dangerLevel.disasterType !== "None" ? `(${dangerLevel.disasterType})` : ""}
                </p>
            </Card.Body>
        </Card>
    );
};

export default DangerLevel;

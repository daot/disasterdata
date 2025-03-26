import React, { useEffect, useState } from 'react';
import { Card } from "react-bootstrap";

const API_HOST = "https://api.disasterdata.duckdns.org";

const TMDT = () => {
    const [topDisaster, setTopDisaster] = useState({ label: '', location: '' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTopDisaster = async () => {
            try {
                const response = await fetch(API_HOST + `/fetch-top-disaster-last-hour`);
                //const response = await fetch('/fetch-top-disaster-last-hour');
                const data = await response.json();
                setTopDisaster(data);
            } catch (error) {
                console.error('Error fetching top disaster:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchTopDisaster();
    }, []);

    if (loading) return <p>Loading...</p>;

    return (
        <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body>
                <Card.Title style={{ fontSize: "0.5rem" }}>Top Mentioned Disaster In The Last 24 Hrs</Card.Title>
                    <p style={{ fontSize: "1.25rem", fontWeight: "bold"}}>
                        {topDisaster.top_label} {topDisaster.top_location ? `(${topDisaster.top_location})` : ""}
                    </p>
            </Card.Body>
        </Card>
    );
};

export default TMDT;

import React, { useEffect, useState } from 'react';
import { Card } from "react-bootstrap";

const API_HOST = process.env.REACT_APP_API_HOST;

const TMDT = () => {
    const [topDisaster, setTopDisaster] = useState({ label: '', location: '' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTopDisaster = async () => {
            try {
                const response = await fetch(API_HOST + `/fetch-top-disaster-location`);
                const data = await response.json();
                console.log('API response:', data);
                setTopDisaster(data);
            } catch (error) {
                console.error('Error fetching top disaster:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTopDisaster();

        const intervalId = setInterval(fetchTopDisaster, 60000);

        return () => clearInterval(intervalId);
    }, []);

    if (loading) return (
        <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body>
                <Card.Title>Top Mentioned Disaster In The Last 24 Hrs</Card.Title>
                    <div style={{ fontSize: "1.25rem"}}>Loading</div>
            </Card.Body>
        </Card>
    );;

    const capitalizeFirstLetter = (str) => {
        return str ? str.charAt(0).toUpperCase() + str.slice(1).toLowerCase() : "";
    };

    return (
        <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body>
                <Card.Title>Top Mentioned Disaster In The Last 24 Hrs</Card.Title>
                    <div style={{ fontSize: "1.25rem"}}>
                        Disaster: {capitalizeFirstLetter(topDisaster.top_label)}, Location: {topDisaster.location ? `(${topDisaster.location})` : ""}
                    </div>
            </Card.Body>
        </Card>
    );
};

export default TMDT;

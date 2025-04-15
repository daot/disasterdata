import React, { useEffect, useState } from 'react';
import { Card } from "react-bootstrap";

const API_HOST = process.env.REACT_APP_API_HOST;

const TMDT = React.memo(({ rangeName, urlQuery }) => {
    const [topDisaster, setTopDisaster] = useState({ label: '', location: '' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTopDisaster = async () => {
            try {
                const response = await fetch(API_HOST + `/fetch-top-disaster-location${urlQuery ? ("?" + urlQuery) : ""}`);
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
    }, [urlQuery]);

    const capitalizeFirstLetter = (str) => {
        return str ? str.charAt(0).toUpperCase() + str.slice(1).toLowerCase() : "";
    };

    return (
        <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body className="d-flex flex-column justify-content-center align-items-start">
                <Card.Title id="current-disaster-title">Top Mentioned Disaster {rangeName}</Card.Title>
                {loading ? (
                    <div id="current-disaster">Loading...</div>
                ) : (
                    <div id="current-disaster">
                        Disaster: {capitalizeFirstLetter(topDisaster.top_label)}, Location: {topDisaster.location ? `(${topDisaster.location})` : ""}
                    </div>
                )}
            </Card.Body>
        </Card>
    );
});

export default TMDT;

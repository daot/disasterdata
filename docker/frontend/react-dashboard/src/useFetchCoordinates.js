import { useEffect, useState } from "react";

const API_HOST = "https://api.disasterdata.duckdns.org";

const useFetchCoordinates = () => {
    const [coordinates, setCoordinates] = useState([]);

    useEffect(() => {
        const fetchCoordinates = async () => {
            try {
                const response = await fetch(API_HOST + "/fetch-location-coordinates/"); // Adjust endpoint as needed
                if (!response.ok) {
                    throw new Error("Failed to fetch coordinates");
                }
                const data = await response.json();
                setCoordinates(data);
            } catch (error) {
                console.error("Error fetching coordinates:", error);
            }
        };

        fetchCoordinates();
    }, []);

    return coordinates;
};

export default useFetchCoordinates;

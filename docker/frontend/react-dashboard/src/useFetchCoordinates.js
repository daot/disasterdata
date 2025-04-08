import { useEffect, useState } from "react";

const API_HOST = process.env.REACT_APP_API_HOST;

const useFetchCoordinates = () => {
  const [coordinates, setCoordinates] = useState([]);

  useEffect(() => {
    const fetchCoordinates = async () => {
      try {
        const response = await fetch(API_HOST + `/fetch-location-coordinates`);
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

    const interval = setInterval(() => {
      fetchCoordinates();
  }, 10000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  return coordinates;
};

export default useFetchCoordinates;

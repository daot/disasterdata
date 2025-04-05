import { useEffect, useState } from "react";

const useFetchCoordinates = () => {
  const [coordinates, setCoordinates] = useState([]);

  useEffect(() => {
    const fetchCoordinates = async () => {
      try {
        const response = await fetch("http://localhost:5000/fetch-location-coordinates");
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

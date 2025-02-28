import { useEffect, useState } from "react";

const useFetchCoordinates = () => {
  const [coordinates, setCoordinates] = useState([]);

  useEffect(() => {
    const fetchCoordinates = async () => {
      try {
        const response = await fetch("/fetch-location-coordinates"); // Adjust endpoint as needed
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


import { useEffect, useState } from "react";

const API_HOST = process.env.REACT_APP_API_HOST;
const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];

const useFetchCoordinates = (selectedDisasterType = "earthquake", urlQuery = "") => {
  const [coordinates, setCoordinates] = useState([]);

  useEffect(() => {
    const fetchCoordinatesForType = async () => {
      const allData = [];

      setCoordinates(allData);
      try {
        let url = `${API_HOST}/fetch-coordinates-by-label?disaster_type=${selectedDisasterType}${urlQuery ? ("&" + urlQuery) : ""}`;

        const response = await fetch(url);
        if (!response.ok) {
          console.warn(`Failed to fetch for ${selectedDisasterType}`);
          return;
        }

        const text = await response.text(); // Get the response as text
        
        // Check if the response contains invalid values like "NaN"
        if (text.includes("NaN") || text.trim() === "") {
          console.error(`Invalid response content for ${selectedDisasterType}:`, text);
          return;
        }

        console.log(`Raw response for ${selectedDisasterType}:`, text); // Log raw response for debugging

        let data = [];
        try {
          data = JSON.parse(text); // Try parsing the JSON
        } catch (e) {
          console.error(`Invalid JSON response for ${selectedDisasterType}:`, e);
          return;
        }

        // Ensure the data is an array and contains valid coordinates
        if (!Array.isArray(data)) {
          console.error(`Invalid data structure for ${selectedDisasterType}:`, data);
          return;
        }

        // Filter out any coordinates with NaN values in lat or lng
        const validCoordinates = data.filter((coord, index) => {
          const isValidLat = !isNaN(coord.lat) && coord.lat !== null && coord.lat !== undefined;
          const isValidLng = !isNaN(coord.lng) && coord.lng !== null && coord.lng !== undefined;

          // Log invalid coordinates for debugging
          if (!isValidLat || !isValidLng) {
            console.warn(`Invalid coordinates at index ${index} for ${selectedDisasterType}:`, coord);
          }

          return isValidLat && isValidLng;
        });

        // Log the valid coordinates after filtering
        console.log(`Valid coordinates for ${selectedDisasterType}:`, validCoordinates);

        allData.push(...validCoordinates);
      } catch (error) {
        console.error(`Error fetching ${selectedDisasterType}:`, error);
      }

      setCoordinates(allData);
    };

    fetchCoordinatesForType();
    const interval = setInterval(fetchCoordinatesForType, 60000); // Refresh every 60 seconds

    return () => clearInterval(interval);
  }, [selectedDisasterType, urlQuery]); // Re-fetch when selectedDisasterType changes

  return coordinates;
};

export default useFetchCoordinates;

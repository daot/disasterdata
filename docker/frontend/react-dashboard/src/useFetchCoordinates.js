import { useEffect, useState } from "react";

const API_HOST = process.env.REACT_APP_API_HOST;
const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];

const useFetchCoordinates = (selectedDisasterType = "earthquake", urlQuery = "") => {
  const [coordinates, setCoordinates] = useState([]);

  useEffect(() => {
    console.log("📡 useFetchCoordinates triggered with:", {
      selectedDisasterType,
      urlQuery,
    });

    const fetchCoordinatesForType = async () => {
      const allData = [];

      try {
        let url = `${API_HOST}/fetch-coordinates-by-label?disaster_type=${selectedDisasterType}${urlQuery ? ("&" + urlQuery) : ""}`;

        console.log(`Fetching coordinates from: ${url}`);

        const response = await fetch(url);
        if (!response.ok) {
          console.warn(`Failed to fetch for ${selectedDisasterType}, status: ${response.status}`);
          return;
        }

        const text = await response.text();

        if (text.includes("NaN") || text.trim() === "") {
          console.error(`Invalid response content for ${selectedDisasterType}:`, text);
          return;
        }

        console.log(`📦 Raw response for ${selectedDisasterType}:`, text);

        let data = [];
        try {
          data = JSON.parse(text);
        } catch (e) {
          console.error(`Invalid JSON response for ${selectedDisasterType}:`, e);
          return;
        }

        if (!Array.isArray(data)) {
          console.error(`Invalid data structure for ${selectedDisasterType}:`, data);
          return;
        }

        const validCoordinates = data.filter((coord, index) => {
          const isValidLat = !isNaN(coord.lat) && coord.lat !== null && coord.lat !== undefined;
          const isValidLng = !isNaN(coord.lng) && coord.lng !== null && coord.lng !== undefined;

          if (!isValidLat || !isValidLng) {
            console.warn(`Invalid coordinates at index ${index} for ${selectedDisasterType}:`, coord);
          }

          return isValidLat && isValidLng;
        });

        console.log(`Valid coordinates for ${selectedDisasterType}:`, validCoordinates);
        allData.push(...validCoordinates);

      } catch (error) {
        console.error(`Error fetching ${selectedDisasterType}:`, error);
      }

      setCoordinates(allData);
    };

    fetchCoordinatesForType();
    const interval = setInterval(fetchCoordinatesForType, 60000); // Refresh every 60 seconds

    return () => {
      console.log("Clearing interval for coordinates refresh");
      clearInterval(interval);
    };
  }, [selectedDisasterType, urlQuery]);

  return coordinates;
};

export default useFetchCoordinates;

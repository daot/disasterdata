import React, { useEffect, useState } from "react";
import WordCloud from "react-d3-cloud";
import { scaleLinear } from "d3-scale";


const API_HOST = "https://api.disasterdata.duckdns.org";

const disasterTypes = ["other", "hurricane", "flood", "wildfire", "tornado", "blizzard"];

const KeywordCloud = ({ selectedDisasterType }) => {
  const [wordData, setWordData] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDataForDisasterType = async (type) => {
      try {
        console.log(`Fetching data for disaster type: ${type}`); // Debugging Log
        const response = await fetch(API_HOST + `/fetch-most-frequent-word/?disaster_type=${type}`);
        if (!response.ok) throw new Error(`Failed to fetch data for ${type}`);

        const data = await response.json();
        console.log(`Fetched data for ${type}:`, data); // Debugging Log

        return {
          [type]: Array.isArray(data)
            ? data.map(({ count, keyword }) => ({
                value: count,
                text: keyword,
              }))
            : [],
        };
      } catch (error) {
        console.error(`Error fetching data for ${type}:`, error);
        return { [type]: [] };
      }
    };

    setLoading(true);
    Promise.all(disasterTypes.map(fetchDataForDisasterType))
      .then((results) => {
        const mergedData = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
        console.log("Final merged word data:", mergedData); // Debugging Log
        setWordData(mergedData);
      })
      .catch((err) => setError("Failed to load keyword cloud"))
      .finally(() => setLoading(false));
  }, []);

  const words = wordData[selectedDisasterType] || [];
  console.log(`Displaying words for ${selectedDisasterType}:`, words); // Debugging Log

  const fontScale = scaleLinear()
    .domain(
      words.length > 0
        ? [Math.min(...words.map((d) => d.value)), Math.max(...words.map((d) => d.value))]
        : [10, 60]
    )
    .range([10, 50]);

  const fontSize = (word) => fontScale(word.value);

  return (
    <div style={{ width: "100%", height: "200px", textAlign: "center" }}>
      {error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : loading ? (
        <p>Loading keyword cloud...</p>
      ) : words.length > 0 ? (
        <WordCloud
          data={words}
          fontSize={fontSize}
          rotate={0}
          padding={3}
          width={400}
          height={200}
        />
      ) : (
        <p>No keywords available for this disaster type.</p>
      )}
    </div>
  );
};

export default KeywordCloud;

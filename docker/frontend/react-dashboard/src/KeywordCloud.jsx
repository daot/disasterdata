import React, { useEffect, useState, useCallback } from "react";
import WordCloud from "react-d3-cloud";
import { scaleLinear } from "d3-scale";

const API_HOST = process.env.REACT_APP_API_HOST;

const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];

const KeywordCloud = React.memo(({ urlQuery, selectedDisasterType }) => {
  const [wordData, setWordData] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [initialLoad, setInitialLoad] = useState(true);

  const fetchDataForDisasterType = useCallback(async () => {
    // Only show loading on initial fetch, not refreshes
    if (initialLoad) {
      setLoading(true);
    }
    
    try {
      const results = await Promise.all(
        disasterTypes.map(async (type) => {
          console.log(`Fetching data for disaster type: ${type}`);
          const response = await fetch(API_HOST + `/fetch-most-frequent-word?disaster_type=${type}${urlQuery ? ("&" + urlQuery) : ""}`);
          if (!response.ok) throw new Error(`Failed to fetch data for ${type}`);

          const data = await response.json();
          console.log(`Fetched data for ${type}:`, data);

          return {
            [type]: Array.isArray(data)
              ? data.map(({ count, keyword }) => ({
                  value: count,
                  text: keyword,
                }))
              : [],
          };
        })
      );

      const mergedData = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
      console.log("Final merged word data:", mergedData);
      setWordData(mergedData);
      setError(null);
    } catch (err) {
      console.error("Error fetching keyword cloud:", err);
      setError("Failed to load keyword cloud");
    } finally {
      setLoading(false);
      if (initialLoad) {
        setInitialLoad(false);
      }
    }
  }, [urlQuery, initialLoad]);

  useEffect(() => {
    fetchDataForDisasterType(); // Initial fetch

    const intervalId = setInterval(() => {
      console.log("Refreshing keyword cloud...");
      fetchDataForDisasterType();
    }, 60000);

    return () => clearInterval(intervalId); // Cleanup interval on unmount
  }, [fetchDataForDisasterType]);

  const words = wordData[selectedDisasterType] || [];
  console.log(`Displaying words for ${selectedDisasterType}:`, words);

  const fontScale = scaleLinear()
    .domain(
      words.length > 0
        ? [Math.min(...words.map((d) => d.value)), Math.max(...words.map((d) => d.value))]
        : [10, 60]
    )
    .range([10, 50]);

  const fontSize = (word) => fontScale(word.value);
  function randomNordColor() {
    const style = getComputedStyle(document.documentElement)
    const colorMap = [
      style.getPropertyValue('--yellow'),
      style.getPropertyValue('--red'),
      style.getPropertyValue('--green'),
      style.getPropertyValue('--orange'),
      style.getPropertyValue('--purple'),
    ];
    
    const randomIndex = Math.floor(Math.random() * colorMap.length);
    return colorMap[randomIndex];
  }

  return (
    <div style={{ width: "100%", height: "200px", textAlign: "center" }}>
      {error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : initialLoad && loading ? (
        <p>Loading keyword cloud...</p>
      ) : words.length > 0 ? (
        <WordCloud
          data={words}
          font="Roboto"
          fontSize={fontSize}
          rotate={0}
          padding={3}
          width={400}
          height={200}
          fill={randomNordColor}
        />
      ) : (
        <p>No keywords available for this disaster type.</p>
      )}
    </div>
  );
});

export default KeywordCloud;

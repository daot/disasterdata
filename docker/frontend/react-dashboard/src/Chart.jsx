import React, { useEffect, useState, useRef } from "react";
import { Pie } from "react-chartjs-2";
import { Card } from "react-bootstrap";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

const API_HOST = process.env.REACT_APP_API_HOST;

ChartJS.register(ArcElement, Tooltip, Legend);

const Graph = React.memo(({ urlQuery }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [forceUpdate, setForceUpdate] = useState(0);
  const chartRef = useRef(null);
  
  // Force a re-render after mount to ensure styles are applied correctly
  useEffect(() => {
    const timer = setTimeout(() => {
      setForceUpdate(prev => prev + 1);
    }, 100);
    return () => clearTimeout(timer);
  }, []);
  
  const fetchPieData = () => {
    setLoading(true);
    setError(null);
    
    fetch(API_HOST + `/fetch-label-count${urlQuery ? ("?" + urlQuery) : ""}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        return response.json();
      })
      .then((result) => {
        console.log("Fetched Data:", result);

        if (result.error || !result.results || result.results.length === 0) {
          throw new Error("No data found");
        }

        const filteredResults = result.results.filter(
          (item) => item.label.toLowerCase() !== 'other'
        );

        if (filteredResults.length === 0) {
          throw new Error("No valid data found after filtering.");
        }

        const labels = filteredResults.map((item) => item.label);
        const values = filteredResults.map((item) => item.percentage);

        // Get current style for consistent rendering
        const currentStyle = getComputedStyle(document.documentElement);
        const colors = [
          currentStyle.getPropertyValue('--red'),
          currentStyle.getPropertyValue('--orange'), 
          currentStyle.getPropertyValue('--yellow'), 
          currentStyle.getPropertyValue('--green'), 
          currentStyle.getPropertyValue('--purple')
        ];
        
        setData({
          labels: labels,
          datasets: [
            {
              data: values,
              backgroundColor: colors,
              borderColor: colors, // Use the same array for consistency
              borderWidth: 1,
              hoverBackgroundColor: colors,
            },
          ],
        });
      })
      .catch((error) => {
        console.error("Fetch Error:", error);
        setError("Failed to load data.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPieData(); // initial fetch
    const intervalId = setInterval(fetchPieData, 60000); // auto-refresh every 60 sec

    return () => clearInterval(intervalId); // cleanup on unmount
  }, [urlQuery, forceUpdate]); // Add forceUpdate as dependency

  // Get current style when rendering options
  const currentStyle = getComputedStyle(document.documentElement);
  const options = {
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          font: { size: 12 },
          color: currentStyle.getPropertyValue('--foreground-color'),
        },
      },
    },
    responsive: true,
    maintainAspectRatio: false,
  };

  return (
    <Card className="shadow-sm" style={{ height: "280px" }}>
      <Card.Body>
        <Card.Title>Which Natural Disasters Dominate?</Card.Title>
        <div style={{ width: "100%", height: "190px", margin: "auto" }}>
          {error ? (
            <p>{error}</p>
          ) : data ? (
            <Pie ref={chartRef} data={data} options={options} />
          ) : (
            <p>{loading ? "Loading chart..." : "No valid data found."}</p>
          )}
        </div>
      </Card.Body>
    </Card>
  );
});

export default Graph;
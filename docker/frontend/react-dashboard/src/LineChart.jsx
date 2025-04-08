import React, { useEffect, useState, useCallback } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

const API_HOST = process.env.REACT_APP_API_HOST;

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const LineChart = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [],
  });

  const getColor = (disasterType) => {
    const colorMap = {
      hurricane: "#6272a4",
      flood: "#50fa7b",
      wildfire: "#ffb86c",
      tornado: "#bd93f9",
      earthquake: "#f1fa8c",
    };
    return colorMap[disasterType] || "#ffffff"; 
  };

  const fetchPostsOverTime = useCallback(async () => {
    const disasterTypes = ["hurricane", "flood", "wildfire", "tornado"];
    const allTimestamps = new Set();
    const tempData = {};
  
    for (const label of disasterTypes) {
      const response = await fetch(API_HOST + `/fetch-posts-over-time?disaster_type=${label}`);
      const data = await response.json();
      tempData[label] = data;
      data.forEach(item => allTimestamps.add(item.timestamp));
    }
  
    const sortedLabels = Array.from(allTimestamps).sort();
  
    const datasets = disasterTypes.map(label => {
      const labelData = tempData[label];
      const dataMap = Object.fromEntries(labelData.map(d => [d.timestamp, d.post_count]));
      const counts = sortedLabels.map(ts => dataMap[ts] || 0);
  
      return {
        label: label.charAt(0).toUpperCase() + label.slice(1),
        data: counts,
        borderColor: getColor(label),
        fill: false,
        tension: 0.1,
      };
    });
  
    setChartData({
      labels: sortedLabels,
      datasets: datasets,
    });
  }, []);
  

  useEffect(() => {
    fetchPostsOverTime(); // Initial fetch

    const intervalId = setInterval(() => {
      console.log("Fetching new data...");
      fetchPostsOverTime(); // Fetch every 60 seconds
    }, 60000); 

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, [fetchPostsOverTime]); 

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          font: { size: 8 },
          color: "white",
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: "Date (Year-Month)", color: "white" },
        ticks: { color: "white" },
        grid: { color: "white" },
      },
      y: {
        title: { display: true, text: "Number of Posts", color: "white" },
        ticks: { color: "white" },
        grid: { color: "white" },
      },
    },
  };

  return (
    <div style={{ width: "450px", height: "350px", margin: "0 auto" }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default LineChart;

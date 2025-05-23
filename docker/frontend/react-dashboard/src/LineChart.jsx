import React, { useEffect, useState, useCallback } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

const API_HOST = process.env.REACT_APP_API_HOST;
const style = getComputedStyle(document.documentElement)

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const LineChart = React.memo(({ urlQuery }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [],
  });

  const getColor = (disasterType) => {
    const colorMap = {
      hurricane: style.getPropertyValue('--yellow'),
      flood: style.getPropertyValue('--red'),
      wildfire: style.getPropertyValue('--green'),
      tornado: style.getPropertyValue('--orange'),
      earthquake: style.getPropertyValue('--purple'),
    };
    return colorMap[disasterType] || style.getPropertyValue('--foreground-color'); 
  };

  const fetchPostsOverTime = useCallback(async () => {
    const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];
    const allTimestamps = new Set();
    const tempData = {};
  
    for (const label of disasterTypes) {
      const response = await fetch(API_HOST + `/fetch-posts-over-time?disaster_type=${label}${urlQuery ? ("&" + urlQuery) : ""}`);
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
  }, [urlQuery]);
  

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
          color: style.getPropertyValue('--foreground-color'),
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: "Date (Year-Month)", color: style.getPropertyValue('--foreground-color') },
        ticks: { color: style.getPropertyValue('--foreground-color') },
        grid: { color: style.getPropertyValue('--foreground-color') },
      },
      y: {
        title: { display: true, text: "Number of Posts", color: style.getPropertyValue('--foreground-color') },
        ticks: { color: style.getPropertyValue('--foreground-color') },
        grid: { color: style.getPropertyValue('--foreground-color') },
      },
    }
  };

  return (
    <div style={{ maxWidth: "450px", width: "100%", height: "100%", margin: "0 auto" }}>
      <Line data={chartData} options={options} />
    </div>
  );
});

export default LineChart;

import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

const API_HOST = "https://api.disasterdata.duckdns.org";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const LineChart = () => {
  const [chartData, setChartData] = useState({
    labels: [], 
    datasets: [] 
  });

  const fetchPostsOverTime = async () => {
    const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];
    const datasets = [];
    const labels = new Set(); 

    for (const label of disasterTypes) {
      const response = await fetch(API_HOST + `/fetch-posts-over-time/?disaster_type=${label}`);
      //const response = await fetch(`/fetch-posts-over-time/?disaster_type=${label}`);
      const data = await response.json();

      data.forEach(item => labels.add(item.timestamp));
 
      const counts = Array.from(labels).map(date => {
        const entry = data.find(item => item.timestamp === date);
        return entry ? entry.post_count : 0;
      });

      datasets.push({
        label: label.charAt(0).toUpperCase() + label.slice(1),
        data: counts,
        borderColor: getColor(label),
        //backgroundColor: color,
        fill: false,
        tension: 0.1,
      });
    }

    const sortedLabels = Array.from(labels).sort();

    setChartData({
      labels: sortedLabels,
      datasets: datasets
    });
  };

  const getColor = (disasterType) => {
    const colorMap = {
      hurricane: "#6272a4",
      flood: "#50fa7b",
      wildfire: "#ffb86c",
      tornado: "#bd93f9",
      blizzard: "#f1fa8c",
    };
    return colorMap[disasterType] || "#ffffff"; // Default to white if not found
  };
  
  
  useEffect(() => {
    fetchPostsOverTime();
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          font: {
            size: 8,
          },
          color: "white",
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Date (Year-Month)",
          color: "white",
        },
        ticks: {
          color: "white",
        },
        grid: {
          color: "white",
        },
      },
      y: {
        title: {
          display: true,
          text: "Number of Posts",
          color: "white"
        },
        ticks: {
          color: "white",
        },
        grid: {
          color: "white",
        },
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

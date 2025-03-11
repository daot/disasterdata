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
    const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "blizzard"];
    const datasets = [];
    const labels = new Set(); 

    for (const label of disasterTypes) {
      const response = await fetch(API_HOST + `/fetch-posts-over-time/?label=${label}`);
      //const response = await fetch(`/fetch-posts-over-time/?label=${label}`);
      const data = await response.json();

      data.forEach(item => labels.add(item.timestamp));
 
      const counts = Array.from(labels).map(month => {
        const monthData = data.find(item => item.timestamp === month);
        return monthData ? monthData.count : 0;
      });

      datasets.push({
        label: label.charAt(0).toUpperCase() + label.slice(1),
        data: counts,
        borderColor: getRandomColor(),
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

  const getRandomColor = () => {
    const letters = "0123456789ABCDEF";
    let color = "#";
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };

  useEffect(() => {
    fetchPostsOverTime();
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Date (Year-Month)",
        },
      },
      y: {
        title: {
          display: true,
          text: "Number of Posts",
        },
      },
    },
  };

  return (
    <div>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default LineChart;

import React, { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Card } from "react-bootstrap";

const API_HOST = "https://api.disasterdata.duckdns.org"

// Register required components for Chart.js
ChartJS.register(ArcElement, Tooltip, Legend);

const Graph = ({ keyword }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!keyword) return;

    fetch(API_HOST + `/fetch-disaster-count/?keyword=${keyword}`)
      .then((response) => response.json())
      .then((result) => {
        console.log("Fetched Data:", result);
        setData({
          labels: ["Matching", "Non-Matching"],
          datasets: [
            {
              data: [100 - result.percentage, result.percentage], // Pie chart values
              backgroundColor: ["#FF6384", "#36A2EB"], // Colors
              hoverBackgroundColor: ["#FF6384", "#36A2EB"],
            },
          ],
        });
        setLoading(false);
      })
      .catch((error) => {
        console.error("Fetch Error:", error);
        setLoading(false);
      });
  }, [keyword]);

  return (
    <Card className="shadow-sm" style={{ height: "400px", margin: "auto" }}>
        <Card.Body>
            <Card.Title> Disaster Pie Chart </Card.Title>
            <div style={{ width: "250px", height: "400px", margin: "auto"}}>
                {data ? <Pie data={data} /> : <p>Loading chart...</p>}
            </div>
        </Card.Body>
    </Card>
  );
};

export default Graph;



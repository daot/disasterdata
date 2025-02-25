import React, { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Card } from "react-bootstrap";

// Register required components for Chart.js
ChartJS.register(ArcElement, Tooltip, Legend);

const Graph = ({ keyword }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!keyword) return;

    fetch(`http://127.0.0.1:5000/fetch-disaster-count/?keyword=${keyword}`)
      .then((response) => response.json())
      .then((result) => {
        console.log("Fetched Data:", result);
        setData({
          labels: ["Matching", "Non-Matching"],
          datasets: [
            {
              data: [result.percentage, 100 - result.percentage], // Pie chart values
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
    <Card className="shadow-sm" style={{ height: "300px", margin: "auto" }}>
        <Card.Body>
            <Card.Title> Disaster Pie Chart </Card.Title>
            <div style={{ width: "250px", height: "225px", margin: "auto"}}>
                {data ? <Pie data={data} /> : <p>Loading chart...</p>}
            </div>
        </Card.Body>
    </Card>
  );
};

export default Graph;



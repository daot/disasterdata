import { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import { Card } from "react-bootstrap";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

const API_HOST = "https://api.disasterdata.duckdns.org";

ChartJS.register(ArcElement, Tooltip, Legend);

const Graph = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(API_HOST + `/fetch-label-count/`)
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

        const labels = result.results.map((item) => item.label);
        const values = result.results.map((item) => item.percentage);

        setData({
          labels: labels,
          datasets: [
            {
              data: values,
              backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
              hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
            },
          ],
        });
      })
      .catch((error) => {
        console.error("Fetch Error:", error);
        setError("Failed to load data.");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card className="shadow-sm" style={{ height: "375px"}}>
      <Card.Body>
        <Card.Title>Disaster Percentage Distribution</Card.Title>
        <div style={{ width: "225px", height: "300px", margin: "auto"}}>
          {data ? <Pie data={data} /> : <p>Loading chart...</p>}
        </div>
      </Card.Body>
    </Card>
  );
};

export default Graph;

import { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import { Card } from "react-bootstrap";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

const API_HOST = process.env.REACT_APP_API_HOST;

ChartJS.register(ArcElement, Tooltip, Legend);

const Graph = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPieData = () => {
    setLoading(true);
    setError(null);

    fetch(API_HOST + `/fetch-label-count`)
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

        const colors = ["#6272a4", "#50fa7b", "#ffb86c", "#bd93f9", "#f1fa8c"];

        setData({
          labels: labels,
          datasets: [
            {
              data: values,
              backgroundColor: colors,
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
  }, []);

  const options = {
    plugins: {
      legend: {
        position: "left",
        labels: {
          font: { size: 10 },
          color: "white",
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
        <div style={{ width: "200px", height: "190px", margin: "auto" }}>
          {loading ? (
            <p>Loading chart...</p>
          ) : error ? (
            <p>{error}</p>
          ) : data ? (
            <Pie data={data} options={options} />
          ) : (
            <p>No valid data found.</p>
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

export default Graph;
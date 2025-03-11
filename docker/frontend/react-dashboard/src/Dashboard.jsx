import { useState, useEffect } from "react";
import { Row, Col, Card, Container, Button, ButtonGroup } from "react-bootstrap";
import KeywordCloud from "./KeywordCloud";
import Chart from "./Chart";
import HeatMap from "./HeatMap";
import LineChart from "./LineChart";
import tweets from "./Feed";

const Dashboard = () => {
  const [selectedDisasterHeatmap, setSelectedDisasterHeatmap] = useState("hurricane");
  const [selectedDisasterKeywordCloud, setSelectedDisasterKeywordCloud] = useState("hurricane");
  const [selectedDisasterFeed, setSelectedDisasterFeed] = useState("hurricane");
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleString());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleString());
    }, 1000); // Update every second

    return () => clearInterval(interval); 
  }, []);

  return (
    <div className="m-0">
      {/* First Row - Stats */}
      <Row className="m-0">
      <Col md={3}>
          <Card className="shadow-sm" style={{ height: "100px" }}>
            <Card.Body>
              <Card.Title>Welcome to Dashboard</Card.Title>
              <p> {`${currentTime}`} </p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="shadow-sm" style={{ height: "100px" }}>
            <Card.Body>
              <Card.Title style={{ fontSize: "0.5rem" }}>Top Mentioned Disaster Type In The Last Hour</Card.Title>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold"}}> Fire </p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="shadow-sm" style={{ height: "100px" }}>
            <Card.Body>
              <Card.Title style={{ fontSize: "0.5rem" }}>Top Mentioned Disaster Location In The Last Hour</Card.Title>
              <p style={{ fontSize: "1.25rem", fontWeight: "bold"}}> Los Angeles, California </p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="shadow-sm" style={{ height: "100px", border: "2px solid red" }}>
            <Card.Body>
              <Card.Title style={{ fontSize: "1rem" }}>Danger Level</Card.Title>
              <p style={{ fontSize: "1.25rem", fontWeight: "bold"}}> High </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Second Row - HeatMap with Dropdown */}
      <Row className="mt-3">
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "350px"}}>
            <Card.Body>
              <Card.Title>Geospacial Sentiment Heatmap</Card.Title>
              <ButtonGroup>
                <Button 
                  variant={selectedDisasterHeatmap === "tornado" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("tornado")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Tornado
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "flood" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("flood")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Flood
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "wildfire" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("wildfire")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Wildfire
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "hurricane" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("hurricane")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Hurricane
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "blizzard" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("blizzard")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Blizzard
                </Button>
              </ButtonGroup>
              <HeatMap selectedDisasterType={selectedDisasterHeatmap} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "350px"}}>
            <Card.Body>
              <Card.Title>Latest Bluesky Posts</Card.Title>

              {/* Disaster Type Buttons */}
              <ButtonGroup className="mb-3">
                <Button
                  variant={selectedDisasterFeed === "hurricane" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("hurricane")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Hurricane
                </Button>
                <Button
                  variant={selectedDisasterFeed === "flood" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("flood")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Flood
                </Button>
                <Button
                  variant={selectedDisasterFeed === "wildfire" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("wildfire")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Wildfire
                </Button>
                <Button
                  variant={selectedDisasterFeed === "tornado" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("tornado")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Tornado
                </Button>
                <Button
                  variant={selectedDisasterFeed === "blizzard" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("blizzard")}
                  style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                >
                  Blizzard
                </Button>
              </ButtonGroup>

              {/* Displaying the Selected Tweet */}
              <Card className="shadow-sm mb-2" style={{ height: "150px" }}>
                <Card.Body>
                  <p><strong>Author:</strong> {tweets[selectedDisasterFeed].author}</p>
                  <p><strong>Text:</strong> {tweets[selectedDisasterFeed].text}</p>
                  <p><strong>Date:</strong> {tweets[selectedDisasterFeed].date}</p>
                </Card.Body>
              </Card>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Third Row - Charts */}
      <Container fluid>
      <Row className="mt-3">
          <Col md={4}>
            <Chart />
          </Col>
          <Col md={4}>
            <Card className="shadow-sm" style={{ height: "240px" }}>
              <Card.Body>
                <Card.Title>Top Natural-Disaster Related Terms</Card.Title>
                <ButtonGroup>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "tornado" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("tornado")}
                    style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                  >
                    Tornado
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "flood" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("flood")}
                    style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                  >
                    Flood
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "wildfire" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("wildfire")}
                    style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                  >
                    Wildfire
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "hurricane" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("hurricane")}
                    style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                  >
                    Hurricane
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "blizzard" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("blizzard")}
                    style={{ padding: "2px 8px", fontSize: "12px", lineHeight: "1.25" }}
                  >
                    Blizzard
                  </Button>
                </ButtonGroup>
                <KeywordCloud selectedDisasterType={selectedDisasterKeywordCloud} />
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
          <Card className="shadow-sm" style={{ height: "240px" }}>
            <Card.Body>
              <Card.Title> Live Disaster Trends</Card.Title>
              <LineChart/>
            </Card.Body>
          </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Dashboard;


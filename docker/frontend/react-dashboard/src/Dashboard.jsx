import { useState, useEffect } from "react";
import { Row, Col, Card, Container, Button, ButtonGroup } from "react-bootstrap";
import KeywordCloud from "./KeywordCloud";
import Chart from "./Chart";
import HeatMap from "./HeatMap";
import LineChart from "./LineChart";
import Feed from "./Feed";
import DangerLevel from "./DangerLevel";
import TMDT from "./TMDT";

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
          <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body>
              <Card.Title>Crisis and Alert</Card.Title>
              <p> {`${currentTime}`} </p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <TMDT />
        </Col>
        <Col md={3}>
          <DangerLevel />
        </Col>
      </Row>

      {/* Second Row - HeatMap with Dropdown */}
      <Container fluid>
      <Row className="mt-3">
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "350px"}}>
            <Card.Body>
              <Card.Title>Geospatial Sentiment Heatmap</Card.Title>
              <ButtonGroup className="button-group">
                <Button 
                  variant={selectedDisasterHeatmap === "tornado" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("tornado")}
                  
                >
                  Tornado
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "flood" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("flood")}
                  
                >
                  Flood
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "wildfire" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("wildfire")}
                  
                >
                  Wildfire
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "hurricane" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("hurricane")}
                  
                >
                  Hurricane
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "earthquake" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("earthquake")}
                  
                >
                  Earthquake
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
              <ButtonGroup className="button-group">
                <Button
                  variant={selectedDisasterFeed === "hurricane" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("hurricane")}
                  
                >
                  Hurricane
                </Button>
                <Button
                  variant={selectedDisasterFeed === "flood" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("flood")}
                  
                >
                  Flood
                </Button>
                <Button
                  variant={selectedDisasterFeed === "wildfire" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("wildfire")}
                  
                >
                  Wildfire
                </Button>
                <Button
                  variant={selectedDisasterFeed === "tornado" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("tornado")}
                  
                >
                  Tornado
                </Button>
                <Button
                  variant={selectedDisasterFeed === "earthquake" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("earthquake")}
                  
                >
                  Earthquake
                </Button>
              </ButtonGroup>

              <Feed selectedDisaster={selectedDisasterFeed} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Third Row - Charts */}
      
      <Row className="mt-3">
          <Col md={3}>
            <Chart />
          </Col>
          <Col md={4}>
            <Card className="shadow-sm" style={{ height: "280px" }}>
              <Card.Body>
                <Card.Title>Top Natural-Disaster Related Terms</Card.Title>
                <ButtonGroup className="button-group">
                  <Button 
                    variant={selectedDisasterKeywordCloud === "tornado" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("tornado")}
                    
                  >
                    Tornado
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "flood" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("flood")}
                    
                  >
                    Flood
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "wildfire" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("wildfire")}
                    
                  >
                    Wildfire
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "hurricane" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("hurricane")}
                    
                  >
                    Hurricane
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "earthquake" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("earthquake")}
                    
                  >
                    Earthquake
                  </Button>
                </ButtonGroup>
                <KeywordCloud selectedDisasterType={selectedDisasterKeywordCloud} />
              </Card.Body>
            </Card>
          </Col>
          <Col md={5}>
          <Card className="shadow-sm" style={{ height: "280px" }}>
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

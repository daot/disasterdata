import { useState } from "react";
import { Row, Col, Card, Container, Dropdown } from "react-bootstrap";
import KeywordCloud from "./KeywordCloud";
import Chart from "./Chart";
import HeatMap from "./HeatMap";

const Dashboard = () => {
  const [selectedDisaster, setSelectedDisaster] = useState("hurricane");

  const handleSelect = (eventKey) => {
    setSelectedDisaster(eventKey);
  };

  return (
    <div className="mt-2">
      {/* First Row - Stats */}
      <Row className="mt-3">
        <Col md={6}>
          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title>Top Mentioned Disaster Type in the last hour</Card.Title>
              <p> Fire </p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title>Top Mentioned Disaster Location in the last hour</Card.Title>
              <p> Los Angeles, California </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Second Row - Charts */}
      <Container fluid>
        <Row className="mt-3">
          <Col md={6}>
            <Chart />
          </Col>
          <Col md={6}>
          <Card className="shadow-sm" style={{ height: "375px"}}>
            <Card.Body>
              <Card.Title>Keyword Cloud</Card.Title>
              <Dropdown onSelect={(eventKey) => setSelectedDisaster(eventKey)}>
                <Dropdown.Toggle variant="primary" id="dropdown-basic">
                  {selectedDisaster === "all" ? "Select Disaster Type" : selectedDisaster.charAt(0).toUpperCase() + selectedDisaster.slice(1)}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="other">Other</Dropdown.Item>
                  <Dropdown.Item eventKey="tornado">Tornado</Dropdown.Item>
                  <Dropdown.Item eventKey="flood">Flood</Dropdown.Item>
                  <Dropdown.Item eventKey="wildfire">Wildfire</Dropdown.Item>
                  <Dropdown.Item eventKey="hurricane">Hurricane</Dropdown.Item>
                  <Dropdown.Item eventKey="blizzard">Blizzard</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              <KeywordCloud selectedDisasterType={selectedDisaster}/>
            </Card.Body>
          </Card>
          </Col>
        </Row>
      </Container>

      {/* Third Row - HeatMap with Dropdown */}
      <Row className="mt-4">
        <Col md={12}>
          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title>Heat Map</Card.Title>
              <Dropdown onSelect={(eventKey) => setSelectedDisaster(eventKey)}>
                <Dropdown.Toggle variant="primary" id="dropdown-basic">
                  {selectedDisaster === "all" ? "Select Disaster Type" : selectedDisaster.charAt(0).toUpperCase() + selectedDisaster.slice(1)}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="other">Other</Dropdown.Item>
                  <Dropdown.Item eventKey="tornado">Tornado</Dropdown.Item>
                  <Dropdown.Item eventKey="flood">Flood</Dropdown.Item>
                  <Dropdown.Item eventKey="wildfire">Wildfire</Dropdown.Item>
                  <Dropdown.Item eventKey="hurricane">Hurricane</Dropdown.Item>
                  <Dropdown.Item eventKey="blizzard">Blizzard</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              <HeatMap selectedDisasterType={selectedDisaster} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;


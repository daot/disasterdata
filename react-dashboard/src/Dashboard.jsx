import { Row, Col, Card } from "react-bootstrap";
//import StatsCard from "./StatsCard";

const Dashboard = () => {
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
      <Row className="mt-3">
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "300px" }}>
            <Card.Body>
              <Card.Title>Chart</Card.Title>
              <img
                src="/graph.png"
                alt="Demo Chart"
                className="img-fluid"
                style={{ height: "250px"}}
              />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "300px" }}>
            <Card.Body>
              <Card.Title>Heat Map</Card.Title>
              <img
                src="/heatmap.png"
                alt="Heat Map"
                className="img-fluid"
                style={{ height: "250px", objectFit: "contain" }}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Third Row - Feed and Extra */}
      <Row className="mt-4">
        <Col md={6}>
          <Card classNmae="shadow-sm" style={{ height: "250px" }}>
            <Card.Body>
              <Card.Title>Keyword Cloud</Card.Title>
              <p>🔥 Fire - <strong>90</strong></p>
              <p>🌪 Tornado - <strong>75</strong></p>
              <p>🌀 Hurricane - <strong>85</strong></p>
              <p>❄️ Blizzard - <strong>60</strong></p>
              <p>🌊 Flood - <strong>80</strong></p>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="shadow-sm" style={{ height: "250px" }}>
            <Card.Body>
              <Card.Title>Feed</Card.Title>
              <p> Oh no! The fire is super big </p>
              <p> Fire! Fire! Fire!</p>
              <p> Prayers for those affected by the fire</p>
              <p> #LAFires</p>
              <p> everything burned down</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;

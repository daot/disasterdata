import { Row, Col, Card, Container } from "react-bootstrap";
import KeywordCloud from "./KeywordCloud";
import Chart from "./Chart";
import HeatMap from "./HeatMap";

const Dashboard = () => {
  const keyword = "disaster"

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
          <Chart keyword={keyword} />
        </Col>
        <Col md={6}>
          <HeatMap />
        </Col>
      </Row>

      
      {/* Third Row - Feed and Extra */}
      <Container fluid>
      <Row className="mt-4">
        <Col md={6}>
          <KeywordCloud />
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
      </Container>
    </div>
  );
};

export default Dashboard;

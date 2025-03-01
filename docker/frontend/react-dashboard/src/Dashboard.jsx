import { Row, Col, Card, Container } from "react-bootstrap";
import KeywordCloud from "./KeywordCloud";
import Chart from "./Chart";
import HeatMap from "./HeatMap";

const Dashboard = () => {
    const keyword = "other";

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
                        <Chart keyword={keyword} />
                    </Col>
                    <Col md={6}>
                        <KeywordCloud />
                    </Col>
                </Row>
            </Container>

            {/* Third Row - Feed and Extra */}
            <Row className="mt-4">
                <Col md={12}>
                    <HeatMap />
                </Col>
            </Row>
        </div>
    );
};

export default Dashboard;

import { Container, Row, Col, Navbar, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";

const Layout = ({ children }) => {
  return (
    <>
      {/* Top Navbar */}
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container fluid>
          <Navbar.Brand as={Link} to="/">Dashboard</Navbar.Brand>
        </Container>
      </Navbar>

      {/* Sidebar and Main Content */}
      <Container fluid>
        <Row className="vh-100"> {/* Full height for the row */}
          {/* Sidebar (Fixed Height & Scrollable) */}
          <Col md={2} className="bg-dark text-white p-3 d-flex flex-column" style={{ height: '150vh' }}>
            <Nav className="flex-column">
              <Nav.Link as={Link} to="/" className="text-white">Home</Nav.Link>
              <Nav.Link as={Link} to="/analytics" className="text-white">Real-Time Analytics</Nav.Link>
            </Nav>
          </Col>

          {/* Main Content Area */}
          <Col md={10} className="p-4" style={{ minHeight: '100vh' }}>
            {children}
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Layout;

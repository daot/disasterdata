import { Container, Row, Col, Navbar, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import "./Layout.css";

const Layout = ({ children }) => {
  return (
    <>
      {/* Sidebar and Main Content */}
      <Container fluid className="d-flex flex-column vh-100"> {/* Ensures it doesn’t shrink too much */}
        <Row className="flex-grow-1">
          {/* Sidebar (Automatic height, no forced full-screen height) */}
          <Col md={1} className="bg-dark text-white p-3">
            <Nav className="flex-column">
              <Nav.Link as={Link} to="/" className="text-white">Home</Nav.Link>
              {/* <Nav.Link as={Link} to="/analytics" className="text-white">Real-Time Analytics</Nav.Link> */}
            </Nav>
          </Col>

          {/* Main Content Area (Adjustable height) */}
          <Col md={11} className="p-4">
            {children}
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Layout;

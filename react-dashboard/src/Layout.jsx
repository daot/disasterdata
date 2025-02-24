import { Container, Row, Col, Navbar, Nav } from "react-bootstrap";

const Layout = ({ children }) => {
  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Navbar.Brand href="#">Dashboard</Navbar.Brand>
        <Nav className="ms-auto">
          <Nav.Link href="#">Profile</Nav.Link>
          <Nav.Link href="#">Logout</Nav.Link>
        </Nav>
      </Navbar>
      <Container fluid>
        <Row>
          <Col md={2} className="bg-dark min-vh-100 p-3">
            <Nav className="flex-column">
              <Nav.Link href="#">Home</Nav.Link>
              <Nav.Link href="#">Analytics</Nav.Link>
              <Nav.Link href="#">Settings</Nav.Link>
            </Nav>
          </Col>
          <Col md={10} className="p-3">
            {children}
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Layout;

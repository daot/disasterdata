import { Container, Row, Col, Navbar, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import "./Layout.css";

const Layout = ({ children }) => {
  return (
    <>
      {/* Sidebar and Main Content */}
      <Container id="main-container" className="d-flex justify-content-center align-items-center min-vh-100 pt-3 pb-3"> {/* Ensures it doesn’t shrink too much */}
        {children}
      </Container>
    </>
  );
};

export default Layout;

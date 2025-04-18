import { Container, Row, Col, Navbar, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import "./Layout.css";

const Layout = ({ children }) => {
  return (
    <>
      {/* Sidebar and Main Content */}
      <Container id="main-container" className="d-flex flex-column justify-content-center align-items-center"> 
        {children}
      </Container>
    </>
  );
};

export default Layout;

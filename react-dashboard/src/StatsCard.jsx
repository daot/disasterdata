import { Card } from "react-bootstrap";

const StatsCard = ({ title, value }) => {
  return (
    <Card className="shadow-sm">
      <Card.Body>
        <Card.Title>{title}</Card.Title>
        <Card.Text className="fs-3">{value}</Card.Text>
      </Card.Body>
    </Card>
  );
};

export default StatsCard;

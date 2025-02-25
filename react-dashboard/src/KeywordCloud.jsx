import React, { useEffect, useState } from "react";
import ReactWordcloud from "react-wordcloud";
import { Card } from "react-bootstrap";
import { fetchWordData } from "./wordData"; // Import fetch function

const KeywordCloud = () => {
  const [words, setWords] = useState([]);

  useEffect(() => {
    fetchWordData().then(setWords);
  }, []);

  return (
    <Card className="shadow-sm" style={{ height: "300px", margin: "auto" }}>
      <Card.Body>
        <Card.Title>Keyword Cloud</Card.Title>
        {words.length > 0 ? (
          <div style={{ height: 300 }}>
            <ReactWordcloud words={words} />
          </div>
        ) : (
          <p>Loading keyword cloud...</p>
        )}
      </Card.Body>
    </Card>
  );
};

export default KeywordCloud;

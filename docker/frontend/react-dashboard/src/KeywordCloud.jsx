import React, { useEffect, useState } from "react";
import WordCloud from "react-d3-cloud";
import { Card } from "react-bootstrap";

const KeywordCloud = () => {
  const [words, setWords] = useState([]);

  useEffect(() => {
    fetch("https://api.disasterdata.duckdns.org" + "/fetch-most-frequent-word/")
      .then((response) => response.json())
      .then((data) => {
        if (data && data["count of each word"]) {
          const formattedWords = data["count of each word"].map(([text, value]) => ({
            text,
            value,
          }));
          setWords(formattedWords);
        }
      })
      .catch((error) => console.error("Error fetching word cloud data:", error));
  }, []);

  return (
    <Card className="shadow-sm" style={{ height: "300px", margin: "auto" }}>
      <Card.Body>
        <Card.Title>Keyword Cloud</Card.Title>
        {words.length > 0 ? (
          <WordCloud
            data={words}
            fontSize={(word) => Math.log2(word.value) * 3}
            rotate={0}
            padding={2}
            width={300}
            height={200}
          />
        ) : (
          <p>Loading keyword cloud...</p>
        )}
      </Card.Body>
    </Card>
  );
};

export default KeywordCloud;

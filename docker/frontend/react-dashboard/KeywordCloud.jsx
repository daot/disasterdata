import React, { useEffect, useState } from "react";
import WordCloud from "react-d3-cloud";
import { Card } from "react-bootstrap";
import { scaleLinear } from "d3-scale";

const KeywordCloud = () => {
  const [words, setWords] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/fetch-most-frequent-word/")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        return response.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          const formattedWords = data.map(({ count, keyword }) => ({
            value: count,
            text: keyword,
          }));
          setWords(formattedWords);
        } else {
          setWords([]);
        }
      })
      .catch((error) => {
        console.error("Error fetching word cloud data:", error);
        setError("Failed to load keyword cloud");
      });
  }, []);

  const fontScale = scaleLinear()
    .domain(
      words.length > 0
        ? [Math.min(...words.map((d) => d.value)), Math.max(...words.map((d) => d.value))]
        : [10, 60]
    )
    .range([10, 60]); // Min and max font sizes

  const fontSize = (word) => fontScale(word.value);

  return (
    <Card className="shadow-sm" style={{ height: "300px", margin: "auto" }}>
      <Card.Body>
        <Card.Title>Keyword Cloud</Card.Title>
        {error ? (
          <p style={{ color: "red" }}>{error}</p>
        ) : words.length > 0 ? (
          <WordCloud
            data={words}
            fontSize={fontSize}
            rotate={0}
            padding={2}
            width={300}
            height={100}
          />
        ) : (
          <p>Loading keyword cloud...</p>
        )}
      </Card.Body>
    </Card>
  );
};

export default KeywordCloud;

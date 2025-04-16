import React, { useEffect, useState } from "react";

const API_HOST = process.env.REACT_APP_API_HOST;


const Feed = React.memo(({ urlQuery, selectedDisaster }) => {
    const [tweets, setTweets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [contentCache, setCache] = useState(<p>Loading tweets...</p>);
    
    useEffect(() => {
        if (!tweets || tweets.length === 0) {
            setCache(<p>No tweets available.</p>);
        } else {
            const sortedTweets = [...tweets]
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .map((tweet, index) =>
                tweet ? (
                    <div key={index} className="tweet">
                    <div className="tweet-header">
                        <a
                        className="tweet-profile-link"
                        href={tweet.url ?? `https://bsky.app/profile/${tweet.handle ?? ""}`}
                        >
                        <strong>@{tweet.handle ?? "Unknown Author"}</strong>
                        <small>
                            {new Date(tweet.timestamp + "Z").toLocaleString('en-US', {
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit',
                            second: '2-digit',
                            hour12: true,
                            }) ?? "No date available"}
                        </small>
                        </a>
                        <br />
                    </div>
                    <div className="tweet-text">
                        {tweet.text ?? "No text available"}
                    </div>
                    </div>
                ) : null
            );
    
        setCache(sortedTweets);
        }
    }, [tweets]);
    
    useEffect(() => {
        const fetchTweets = async () => {

        const disasterTypes = ["hurricane", "flood", "wildfire", "tornado", "earthquake"];

            if (!selectedDisaster || !disasterTypes.includes(selectedDisaster)) {
                console.warn("Invalid or missing disaster type:", selectedDisaster);
                return;
            }

            setLoading(true);
            setError(null);

            try {
                console.log(`Fetching tweets for disaster type: ${selectedDisaster}`);
                const response = await fetch(API_HOST + `/fetch-text-from-label?disaster_type=${selectedDisaster}${urlQuery ? ("&" + urlQuery) : ""}`);

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                console.log("API Response:", data);

                if (!Array.isArray(data) || data.length === 0) {
                    setTweets([]);
                    setError("No tweets found for this disaster type.");
                } else {
                    setTweets(data);
                }
            } catch (error) {
                console.error("Error fetching tweets:", error);
                setError("Failed to fetch tweets. Please try again.");
                setTweets([]);
            } finally {
                setLoading(false);
            }
        };

        fetchTweets();

        const intervalId = setInterval(fetchTweets, 60000);

        return () => clearInterval(intervalId);
    }, [urlQuery, selectedDisaster]);

    return (
        <div>
          <div className="tweet-container mt-3">
            {contentCache}
          </div>
        </div>
      );
  
});

export default Feed;
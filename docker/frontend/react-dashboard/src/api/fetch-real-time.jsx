import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Timeline = () => {
  const [posts, setPosts] = useState([]);  // To store fetched posts
  const [loading, setLoading] = useState(true);  // To show a loading state while fetching

  // Fetch posts from Flask API
  useEffect(() => {
    axios.get('http://127.0.0.1:5000/view-feed/')
      .then(response => {
        setPosts(response.data);  // Store posts in state
        setLoading(false);  // Hide loading indicator
      })
      .catch(error => {
        console.error("There was an error fetching the posts:", error);
      });
  }, []);

  return ( 
    <div>
    {loading ? (
      <p>loading posts...</p>  /* Correctly placed comment */
    ) : (
      <div>
        {posts.map(post => (
          <div key={post.id} className="post">
            <h3>{post.author} (@{post.handle})</h3>
            <p>{post.text}</p>
          </div>
        ))}
      </div>
    )}
  </div>)
}

export default Timeline;
import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
// Connect to Flask server via WebSocket
const socket = io('http://127.0.0.1:5000');

const RealTimeBlueskyFeed = () => {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    // Listen for new data emitted by Flask backend
    socket.on('new_data', (newPosts) => {
      setPosts(newPosts);
    });

    // Cleanup the socket connection when the component unmounts
    return () => {
      socket.off('new_data');
    };
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">Real-Time Bluesky Feed</h2>
      {/* Render posts */}
      <div>
        {posts.map((post, index) => (
          <div key={index}>
            <h3>{post.author}</h3>
            <p>{post.text}</p>
            <p>Likes: {post.likes}</p>
            <hr />
          </div>
        ))}
      </div>
      </div>
  );
};
export default RealTimeBlueskyFeed
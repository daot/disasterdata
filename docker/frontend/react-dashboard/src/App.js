// App.js
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import Dashboard from "./Dashboard";
import Timeline from "./api/fetch-real-time.jsx"
import BlueskyFeed from "./api/makeContinuousFeed.jsx";
import RealTimeAnalytics from "./RealTimeAnalytics";

function App() {
  return (
    <Router>
        <Routes>
          <Route path ="/" element={<Layout><Dashboard /></Layout>} />
          <Route path ="/analytics" element={<Layout><RealTimeAnalytics /></Layout>} />  
        </Routes>
    </Router>
  );
}

export default App;




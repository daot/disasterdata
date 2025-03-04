// App.js

import Layout from "./Layout";
import Dashboard from "./Dashboard";
import Timeline from "./api/fetch-real-time.jsx"
import BlueskyFeed from "./api/makeContinuousFeed.jsx";

function App() {
    return (
        <Layout>
            <Dashboard />
        </Layout>
    );
}

export default App;

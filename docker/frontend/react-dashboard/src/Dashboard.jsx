import { useState, useEffect } from "react";
import { Row, Col, Card, Container, Button, ButtonGroup } from "react-bootstrap";
import KeywordCloud from "./KeywordCloud";
import Chart from "./Chart";
import HeatMap from "./HeatMap";
import LineChart from "./LineChart";
import Feed from "./Feed";
import DangerLevel from "./DangerLevel";
import TMDT from "./TMDT";

const Dashboard = () => {
  const [filterRange, setFilterRange] = useState("day");
  const [selectedDisasterHeatmap, setSelectedDisasterHeatmap] = useState("hurricane");
  const [selectedDisasterKeywordCloud, setSelectedDisasterKeywordCloud] = useState("hurricane");
  const [selectedDisasterFeed, setSelectedDisasterFeed] = useState("hurricane");
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleString());
  const [urlQuery, setUrlQuery] = useState('');
  const [rangeName, setRangeName] = useState('in the Past Day');
  const [customRangeFrom, setCustomRangeFrom] = useState('');
  const [customRangeTo, setCustomRangeTo] = useState('');

  useEffect(() => {
    const now = new Date();
        let start = null;
        let end = new Date();
    
        switch (filterRange) {
          case 'hour':
            start = new Date(now);
            start.setHours(start.getHours() - 1);
            setRangeName('in the Past Hour');
            break;
          case 'day':
            start = new Date(now);
            start.setDate(start.getDate() - 1);
            setRangeName('in the Past Day');
            break;
          case 'week':
            start = new Date(now);
            start.setDate(start.getDate() - 7);
            setRangeName('in the Past Week');
            break;
          case 'month':
            start = new Date(now);
            start.setMonth(start.getMonth() - 1);
            setRangeName('in the Past Month');
            break;
          case 'year':
            start = new Date(now);
            start.setFullYear(start.getFullYear() - 1);
            setRangeName('in the Past Year');
            break;
          case 'custom':
            const customStart = new Date(customRangeFrom);
            const customEnd = new Date(customRangeTo);
            if (
              !isNaN(customStart.getTime()) &&
              !isNaN(customEnd.getTime()) &&
              customStart <= customEnd
            ) {
              start = customStart;
              end = customEnd;
              setRangeName('from ' + customRangeFrom + ' to ' + customRangeTo);
            } else {
              console.warn('Invalid custom date range');
              start = new Date(0);
              end = new Date("2262-04-10 23:47:16.854775807Z");
              setRangeName('of All Time');
            }
            break;
          default:
            start = null;
            end = null;
        }

        if (start && end) {
            const query = `start_date=${encodeURIComponent(start.toISOString())}&end_date=${encodeURIComponent(end.toISOString())}`;
            setUrlQuery(query);
        } else {
            setUrlQuery('');
        }

    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleString());
    }, 1000); // Update every second

    return () => clearInterval(interval); 
  }, [filterRange, customRangeFrom, customRangeTo]);

  return (
    <div className="m-0">
      {/* Filter Row */}
    <Container fluid>
    <Row className="m-0 d-flex">
      <Card className="shadow-sm">
        <Card.Body className="d-flex justify-content-center">
          <Card.Title className="m-0" style={{paddingRight: "12px"}}>Filter By:</Card.Title>
          <ButtonGroup className="button-group">
            <Button 
              variant={filterRange === "hour" ? "primary" : "outline-primary"} 
              onClick={() => setFilterRange("hour")}
              
            >
              Hour
            </Button>
            <Button 
              variant={filterRange === "day" ? "primary" : "outline-primary"} 
              onClick={() => setFilterRange("day")}
              
            >
              Day
            </Button>
            <Button 
              variant={filterRange === "week" ? "primary" : "outline-primary"} 
              onClick={() => setFilterRange("week")}
              
            >
              Week
            </Button>
            <Button 
              variant={filterRange === "month" ? "primary" : "outline-primary"} 
              onClick={() => setFilterRange("month")}
              
            >
              Month
            </Button>
            <Button 
              variant={filterRange === "year" ? "primary" : "outline-primary"} 
              onClick={() => setFilterRange("year")}
              
            >
              Year
            </Button>
            <Button 
              variant={filterRange === "custom" ? "primary" : "outline-primary"} 
              onClick={() => setFilterRange("custom")}
              
            >
              Custom:
            </Button>
          </ButtonGroup>
          <div className="input-group m-0 justify-content-center align-items-start" style={{ width: "200px", paddingLeft: "12px"}}>
            <input 
              id="custom-range-from" 
              className="form-control" 
              type="text" 
              placeholder="From:"
              value={customRangeFrom}
              onChange={(e) => setCustomRangeFrom(e.target.value)}
            />
            <input 
              id="custom-range-to" 
              className="form-control" 
              type="text" 
              placeholder="To:"
              value={customRangeTo}
              onChange={(e) => setCustomRangeTo(e.target.value)}
            />
          </div>
        </Card.Body>
      </Card>
    </Row>
      {/* First Row - Stats */}
      <Row className="mt-3 d-flex">
        <Col md={3} className="flex-shrink-1">
          <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body className="d-flex flex-column justify-content-center align-items-start">
              <Card.Title id="current-time-title">Dashboard</Card.Title>
              <div id="current-time"> {`${currentTime}`} </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} className="flex-grow-1">
          <TMDT rangeName={rangeName} urlQuery={urlQuery}/>
        </Col>
        <Col md={3} className="flex-shrink-1">
          <DangerLevel urlQuery={urlQuery}/>
        </Col>
      </Row>

      {/* Second Row - HeatMap with Dropdown */}
      <Row className="mt-3">
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "350px"}}>
            <Card.Body>
              <Card.Title>Geospatial Sentiment Heatmap</Card.Title>
              <ButtonGroup className="button-group">
                <Button 
                  variant={selectedDisasterHeatmap === "tornado" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("tornado")}
                  
                >
                  Tornado
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "flood" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("flood")}
                  
                >
                  Flood
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "wildfire" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("wildfire")}
                  
                >
                  Wildfire
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "hurricane" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("hurricane")}
                  
                >
                  Hurricane
                </Button>
                <Button 
                  variant={selectedDisasterHeatmap === "earthquake" ? "primary" : "outline-primary"} 
                  onClick={() => setSelectedDisasterHeatmap("earthquake")}
                  
                >
                  Earthquake
                </Button>
              </ButtonGroup>
              <HeatMap urlQuery={urlQuery} selectedDisasterType={selectedDisasterHeatmap} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm" style={{ height: "350px"}}>
            <Card.Body>
              <Card.Title>Latest Bluesky Posts</Card.Title>

              {/* Disaster Type Buttons */}
              <ButtonGroup className="button-group">
                <Button
                  variant={selectedDisasterFeed === "hurricane" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("hurricane")}
                  
                >
                  Hurricane
                </Button>
                <Button
                  variant={selectedDisasterFeed === "flood" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("flood")}
                  
                >
                  Flood
                </Button>
                <Button
                  variant={selectedDisasterFeed === "wildfire" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("wildfire")}
                  
                >
                  Wildfire
                </Button>
                <Button
                  variant={selectedDisasterFeed === "tornado" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("tornado")}
                  
                >
                  Tornado
                </Button>
                <Button
                  variant={selectedDisasterFeed === "earthquake" ? "primary" : "outline-primary"}
                  onClick={() => setSelectedDisasterFeed("earthquake")}
                  
                >
                  Earthquake
                </Button>
              </ButtonGroup>

              <Feed urlQuery={urlQuery} selectedDisaster={selectedDisasterFeed} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Third Row - Charts */}
      
      <Row className="mt-3 d-flex">
          <Col className="flex-grow-1" md={3}>
            <Chart urlQuery={urlQuery}/>
          </Col>
          <Col className="flex-grow-1" md={4}>
            <Card className="shadow-sm" style={{ height: "280px" }}>
              <Card.Body>
                <Card.Title>Top Natural-Disaster Related Terms</Card.Title>
                <ButtonGroup className="button-group">
                  <Button 
                    variant={selectedDisasterKeywordCloud === "tornado" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("tornado")}
                    
                  >
                    Tornado
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "flood" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("flood")}
                    
                  >
                    Flood
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "wildfire" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("wildfire")}
                    
                  >
                    Wildfire
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "hurricane" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("hurricane")}
                    
                  >
                    Hurricane
                  </Button>
                  <Button 
                    variant={selectedDisasterKeywordCloud === "earthquake" ? "primary" : "outline-primary"} 
                    onClick={() => setSelectedDisasterKeywordCloud("earthquake")}
                    
                  >
                    Earthquake
                  </Button>
                </ButtonGroup>
                <KeywordCloud urlQuery={urlQuery} selectedDisasterType={selectedDisasterKeywordCloud} />
              </Card.Body>
            </Card>
          </Col>
          <Col id="linechart-s" md={5}>
          <Card className="shadow-sm" style={{ height: "280px" }}>
            <Card.Body>
              <Card.Title> Live Disaster Trends</Card.Title>
              <LineChart urlQuery={urlQuery}/>
            </Card.Body>
          </Card>
          </Col>
        </Row>
        <Row className="mt-3 d-flex">
        <Col id="linechart-l" className="flex-grow-1">
        <Card className="shadow-sm" style={{ height: "280px" }}>
          <Card.Body>
            <Card.Title> Live Disaster Trends</Card.Title>
            <LineChart urlQuery={urlQuery}/>
          </Card.Body>
        </Card>
        </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Dashboard;


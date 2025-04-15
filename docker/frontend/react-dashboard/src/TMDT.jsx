import React, { useEffect, useState } from 'react';
import { Card } from "react-bootstrap";

const API_HOST = process.env.REACT_APP_API_HOST;

Date.prototype.getWeek = function (dowOffset) {
/*getWeek() was developed by Nick Baicoianu at MeanFreePath: http://www.meanfreepath.com */

    dowOffset = typeof(dowOffset) == 'number' ? dowOffset : 0; //default dowOffset to zero
    var newYear = new Date(this.getFullYear(),0,1);
    var day = newYear.getDay() - dowOffset; //the day of week the year begins on
    day = (day >= 0 ? day : day + 7);
    var daynum = Math.floor((this.getTime() - newYear.getTime() - 
    (this.getTimezoneOffset()-newYear.getTimezoneOffset())*60000)/86400000) + 1;
    var weeknum;
    //if the year starts before the middle of a week
    if(day < 4) {
        weeknum = Math.floor((daynum+day-1)/7) + 1;
        if(weeknum > 52) {
            const nYear = new Date(this.getFullYear() + 1,0,1);
            let nday = nYear.getDay() - dowOffset;
            nday = nday >= 0 ? nday : nday + 7;
            /*if the next year starts before the middle of
              the week, it is week #1 of that year*/
            weeknum = nday < 4 ? 1 : 53;
        }
    }
    else {
        weeknum = Math.floor((daynum+day-1)/7);
    }
    return weeknum;
};

const TMDT = React.memo(({ filterRange }) => {
    const [topDisaster, setTopDisaster] = useState({ label: '', location: '' });
    const [loading, setLoading] = useState(true);
    const [startRange, setStartRange] = useState(null);
    const [endRange, setEndRange] = useState(null);
    const [urlQuery, setUrlQuery] = useState('');
    const [rangeName, setRangeName] = useState('Day');
    const startFilter = "april 10, 2025"
    const endFilter = "april 12, 2025"

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
            start.setWeek(start.getWeek() - 1);
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
            const customStart = new Date(startFilter);
            const customEnd = new Date(endFilter);
            if (
              !isNaN(customStart.getTime()) &&
              !isNaN(customEnd.getTime()) &&
              customStart <= customEnd
            ) {
              start = customStart;
              end = customEnd;
            } else {
              console.warn('Invalid custom date range');
              start = null;
              end = null;
            }
            setRangeName('from ' + start.toLocaleDateString() + ' to ' + end.toLocaleDateString());
            break;
          default:
            start = null;
            end = null;
        }
    
        setStartRange(start);
        setEndRange(end);

        if (start && end) {
            const query = `?start_date=${encodeURIComponent(start.toISOString())}&end_date=${encodeURIComponent(end.toISOString())}`;
            setUrlQuery(query);
        } else {
            setUrlQuery('');
        }

        const fetchTopDisaster = async () => {
            try {
                const response = await fetch(API_HOST + `/fetch-top-disaster-location` + urlQuery);
                const data = await response.json();
                console.log('API response:', data);
                setTopDisaster(data);
            } catch (error) {
                console.error('Error fetching top disaster:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTopDisaster();

        const intervalId = setInterval(fetchTopDisaster, 60000);

        return () => clearInterval(intervalId);
    }, [filterRange, startFilter, endFilter]);

    const capitalizeFirstLetter = (str) => {
        return str ? str.charAt(0).toUpperCase() + str.slice(1).toLowerCase() : "";
    };

    return (
        <Card className="shadow-sm" style={{ height: "100px"}}>
            <Card.Body className="d-flex flex-column justify-content-center align-items-start">
                <Card.Title id="current-disaster-title">Top Mentioned Disaster {rangeName}</Card.Title>
                {loading ? (
                    <div id="current-disaster">Loading...</div>
                ) : (
                    <div id="current-disaster">
                        Disaster: {capitalizeFirstLetter(topDisaster.top_label)}, Location: {topDisaster.location ? `(${topDisaster.location})` : ""}
                    </div>
                )}
            </Card.Body>
        </Card>
    );
});

export default TMDT;

**Flask-React run tutorial**
1. ensure that npm and node.js are installed on computer
   if not, use command **npm install -g npm**
2. within the disasterdata dashboard branch, create a virtual environment with command python3 -m venv <environment_name>
3. use command **pip install flask flask_cors nltk pandas geopy** to install flask dependencies
2. These dependencies should already be in the react-dashboard but if not:
	**npm install chart.js react-d3-cloud react-chartjs-2**
   	or **npm install --save --legacy-peer-deps chart.js react-d3-cloud react-chartjs-2** to bypass dependency tree issue

**Running Backend:**
1. Change to backend directory
2. Connect to env 
4. Open a new  terminal
5. Use command **python main.py** to run flask

**Running Frontend**
1. open another terminal
2. change directory to react-dashboard
3. use command npm start

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_posts():
    # Get the search term (query) from the URL parameters
    searchword = request.args.get('searchword', '')  # Default to empty string if not provided

    # Prepare the payload with the correct parameter 'q'
    params = {'q': searchword}  # Use params instead of json for GET requests

    # Send the GET request to the API endpoint (direct external API call)
    try:
        response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts', params=params)
        response.raise_for_status()  # Raises an exception for 4xx/5xx HTTP errors
        
        # Parse the JSON response from the API
        data = response.json()

        # Return the data received from the external API to the client
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        # Handle errors and return a message with the error
        return jsonify({'error': str(e)}), 500  # Return an HTTP 500 error with the error message

if __name__ == '__main__':
    app.run(debug=True)



import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def search_posts():
    # Set the search word directly in the code
    searchword = 'fire'  # Example of a hardcoded search term

    # Log the search word or print it for debugging
    print(f"Search word: {searchword}")  # This will log the search word in the console

    # Prepare the payload with the correct parameter 'q'
    params = {'q': searchword}  # Use params instead of json for GET requests

    # Send the GET request to the API endpoint (direct external API call)
    try:
        response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts', params=params)
        response.raise_for_status()  # Raises an exception for 4xx/5xx HTTP errors
        
        # Parse the JSON response from the API
        data = response.json()

        # Return the data received from the external API to the client, along with the search word
        return jsonify({'searchword': searchword, 'data': data})

    except requests.exceptions.RequestException as e:
        # Handle errors and return a message with the error
        return jsonify({'error': str(e)}), 500  # Return an HTTP 500 error with the error message

if __name__ == '__main__':
    app.run(debug=True)









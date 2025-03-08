from flask import Flask, jsonify
from flask_cors import CORS
from atproto import Client
import json

app = Flask(__name__)
CORS(app)

try:
    client = Client()
    client.login('ahsuna.bajracharya@gmail.com', '4A3s6h9n0a')
    print("Login Successful")
except exception as e:
    print(f"Login unsuccessful: {e} ")

class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ensure_ascii=False, **kwargs)

app.json_encoder = CustomJSONEncoder

@app.route("/fetch-timeline/", methods=["GET"])
def get_timeline():
    data = client.get_timeline(limit=3)
    feed = data.feed
    new_posts = []
    for p in feed:
        id = p.post.uri
        text = p.post.record.text
        author = p.post.author.display_name
        handle = p.post.author.handle
        new_posts.append({
            "id": id,
            "text": text,
            "author": author,
            "handle": handle
        })
    return jsonify(new_posts)

    """def search_posts():
       data = await client.app.bsky.feed.searchPosts(
        {
        "q": "lahaina fires"
        }
    )"""
@app.route("/view-feed/", methods=["GET"])
def view_feed():
    data = client.app.bsky.feed.get_feed(
        {
            'feed': "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot",
            'limit': 30
        }
    )
    feed = data.feed
    new_posts = []
    for p in feed:
        id = p.post.uri
        text = p.post.record.text
        author = p.post.author.display_name
        handle = p.post.author.handle
        new_posts.append({
            "id": id,
            "text": text,
            "author": author,
            "handle": handle
        })
    return jsonify(new_posts)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





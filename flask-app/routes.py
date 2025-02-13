from application import app
from flask import render_template
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'myproject.env'))
username = os.getenv("BLUESKY_USER")
password = os.getenv("BLUESKY_PASS")

client = Client()
client.login(username, password)

def get_feed():
    data = client.app.bsky.feed.get_feed({
    'feed': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot',
    'limit': 2,
    }, headers={'Accept-Language': 'en'})

    posts = []
    for post in data.feed:
        post_details = {
            'text': post.post.record.text,
            'author': post.post.author.handle,
            #'location': post.post.record.location
        }
        posts.append(post_details)
    return posts

@app.route('/')
@app.route('/index')
def index():
    posts = get_feed()
    return render_template('index.html', posts = posts)
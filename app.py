import os
import flask
import re
from dotenv import load_dotenv

app = flask.Flask(__name__)
load_dotenv()

# https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
app.secret_key = os.getenv("SECRETKEY")

@app.route('/', methods=["POST", "GET"])
def index():
    return flask.render_template("index.html", head_title="Watch 52")


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)

import datetime
import imdb
import os
import random
import requests
import todoist

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
load_dotenv()
ia = imdb.IMDb()
session_movies = []

# https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
app.secret_key = os.getenv("SECRET_KEY")
head_title = "Welcome to Watch 52!"


@app.route("/add-todoist", methods=["POST", "GET"])
def add_todoist():
    if request.method == "POST":
        try:
            todoist_auth_url = "https://todoist.com/oauth/authorize" + \
                f"?client_id={os.getenv('TODOIST_CLIENT_ID')}" + \
                f"&scope=data:read_write&state={app.secret_key}"
            return redirect(todoist_auth_url)
        except Exception as e:
            return redirect(url_for("error", error=e))


def generate_movie_data(top_movies, random_numbers):
    today = datetime.date.today()
    week_number = 1
    movie_data = []

    for n in random_numbers:
        due = today + datetime.timedelta(days=7*week_number)
        movie_data.append(
            {
                "due_date": str(due),
                "rating": top_movies[n]["rating"],
                "title": top_movies[n]["title"],
                "week": week_number,
                "year": top_movies[n]["year"],
            })
        week_number += 1

    return movie_data


def get_movie_data():
    top_movies = ia.get_top250_movies()
    random_numbers = random.sample(range(250), 52)
    movie_data = generate_movie_data(top_movies, random_numbers)
    return movie_data


@app.route("/movies", methods=["POST", "GET"])
def search_imdb():
    if request.method == "POST":
        try:
            movie_data = get_movie_data()
            session['movie_data'] = movie_data
        except imdb.IMDbError as e:
            return redirect(url_for("error", error=e))
        except Exception as e:
            return redirect(url_for("error", error=e))

        return render_template("movies.html",
                               head_title="Your Movies",
                               movies=movie_data)
    else:
        return redirect("/")


def fetch_access_token(code):
    url = 'https://todoist.com/oauth/access_token'
    todoist_auth_data = {
        'client_id': os.getenv("TODOIST_CLIENT_ID"),
        'client_secret': os.getenv("TODOIST_CLIENT_SECRET"),
        'code': code
    }

    try:
        response = requests.post(url, data=todoist_auth_data)
        response = response.json()
        access_token = response["access_token"]
        return access_token
    except Exception as e:
        return redirect(url_for("error", error=e))


@app.route('/todoist-success', methods=["POST", "GET"])
def todoist_success():
    state = request.args.get("state")
    if state != app.secret_key:
        return render_template("error.html",
                               head_title=head_title,
                               error="authorization error")

    try:
        access_token = fetch_access_token(request.args.get("code"))
    except Exception:
        return render_template("error.html",
                               head_title=head_title,
                               error="authorization error")

    if "movie_data" in session:
        api = todoist.TodoistAPI(access_token)
        project = api.projects.add("watch-52")

        for m in session['movie_data']:
            api.items.add(m["title"],
                          project_id=project['id'],
                          due={'string': m["due_date"]})
        api.commit()
    else:
        return render_template("error.html",
                               head_title=head_title,
                               error="session error")

    return render_template("success.html",
                           head_title="Your Todoist tasks are created.")


@app.route('/error', methods=["POST", "GET"])
def error():
    error = request.args["error"]
    return render_template("error.html", head_title=head_title, error=error)


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html", head_title=head_title)


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)

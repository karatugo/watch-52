import os
import re
import imdb
import random
import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify
import todoist
import requests

app = Flask(__name__)
load_dotenv()
ia = imdb.IMDb()

# https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/add-todoist", methods=["POST", "GET"])
def add_todoist():
    if request.method == "POST":
        try:
            test_token = os.getenv("TODOIST_TEST_TOKEN")
            todoist_auth_url = "https://todoist.com/oauth/authorize?client_id=" + os.getenv("TODOIST_CLIENT_ID") +"&scope=data:read,data:delete&state=" + app.secret_key
            return redirect(todoist_auth_url)
        except Exception as e:
            print(e)
            return "fail"


def generate_movie_data(top_movies, random_numbers):
    today = datetime.date.today()
    week_number = 1
    movie_data = []
    for n in random_numbers:
        movie_data.append(
            {
            "week": week_number,
            "title": top_movies[n],
            "due_date": today + datetime.timedelta(days=7*week_number)
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
        except imdb.IMDbError as e:
            return redirect(url_for("error", error=e))
        except Exception as e:
            return redirect(url_for("error", error=e))

        return render_template("movies.html", head_title="Your Movies", movies=movie_data)
    else:
        return redirect("/")

@app.route('/todoist-success', methods=["POST", "GET"])
def todoist_success():
    print(request)
    state = request.args.get("state")
    code = request.args.get("code")
    # api = todoist.TodoistAPI(request["code"])
    # project = api.projects.add("watch-52")
    # task = api.items.add('task', project_id=project['id'])
    # task.update(due={'string': 'tomorrow at 1:00'})
    # api.commit()
    return render_template("success.html", head_title="Your Todoist tasks are created.")

@app.route('/error', methods=["POST", "GET"])
def error():
    error = request.args["error"]
    return render_template("error.html", head_title="Watch 52", error=error)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html", head_title="Watch 52")


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)

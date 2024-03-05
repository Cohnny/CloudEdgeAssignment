import sqlite3
import secrets
import pyodbc
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect, session
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# Generates hexadecimal string.
secret_key = secrets.token_hex(32)
app.secret_key = secret_key
# Adds bcrypt hashing.
bcrypt = Bcrypt(app)


# Define database variable.
DATABASE = 'CloudEdgeAssignment-database.db'
# Database connection.
connection = sqlite3.connect(DATABASE, check_same_thread=False)
# Database cursor.
cursor = connection.cursor()


'''
# Commented code handles azure SQL database connection.
load_dotenv()
# Defines database related variables
database_driver = os.getenv('DATABASE_DRIVER')
database_server = os.getenv('DATABASE_SERVER')
database_name = os.getenv('DATABASE_NAME')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')

# Connect to database using provided credentials
connection_string = (
    f'Driver={{{database_driver}}};'
    f'Server={{{database_server}}};'
    f'Database={{{database_name}}};'
    f'Uid={{{database_user}}};'
    f'Pwd={{{database_password}}};'
    'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)
# Database connection
connection = pyodbc.connect(connection_string)
# Database cursor
cursor = connection.cursor()
'''


# Retrieve all data from the movies table in the database.
def get_all_movies():
    cursor.execute("SELECT title, rating, user_id FROM movies")
    movie_list_db = cursor.fetchall()
    movie_list = add_all_movies_to_dict(movie_list_db)
    return movie_list


# Converts a list of movie data tuples from the database to a more readable dictionary format.
# Each tuple in movies_list is assumed to contain (title, rating, userid).
def add_all_movies_to_dict(movies_list):
    temp_movies = []
    for movie in movies_list:
        title, rating, userid = movie
        cursor.execute("SELECT user_name FROM users WHERE user_id=?", (userid,))
        user_data = cursor.fetchone()
        username = user_data[0]
        movie_to_add = {"title": title, "rating": rating, "username": username}
        temp_movies.append(movie_to_add)
    return temp_movies


# Retrieve all data from the movies table in the database, for a specific user.
def get_movies(user_id):
    cursor.execute("SELECT title, rating, info FROM movies WHERE user_id=?", (user_id,))
    movie_list_db = cursor.fetchall()
    movie_list = add_movies_to_dict(movie_list_db)
    return movie_list


# Converts a list of movie data tuples from the database to a more readable dictionary format.
# Each tuple in movies_list is assumed to contain (title, rating, info).
def add_movies_to_dict(movies_list):
    temp_movies = []
    for movie in movies_list:
        title, rating, info = movie
        movie_to_add = {"title": title, "rating": rating, "info": info}
        temp_movies.append(movie_to_add)
    return temp_movies


# Renders welcome page
@app.route("/")
def index():
    return render_template("welcome.html")


# Gets userid, user movies dict, all movies dict and renders movies page.
@app.route("/movies", methods=["GET"])
def movies():
    userid = session["userid"]
    movie_list = get_movies(userid)
    all_movies_list = get_all_movies()

    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    return render_template('movies.html',
                           movie_list=movie_list,
                           all_movies_list=all_movies_list,
                           sucess_message=success_message,
                           error_message=error_message)


# Retrieves userinput for movie title, rating and description. Gets userid from session and tries to make an INSERT
# call to the database.
@app.route("/add_movies", methods=["POST"])
def add_movies():
    movie_title = request.form["title"]
    movie_rating = request.form["rating"]
    print(movie_rating)
    if (movie_rating.isnumeric() or movie_rating != "") and (movie_title is not None and movie_title != ""):
        movie_rating = int(movie_rating)
        if movie_rating > 100:
            movie_rating = 100
        elif movie_rating < 1:
            movie_rating = 1
        movie_info = request.form["info"]
        user_id = session["userid"]

        # If the movie already exists in the database an exception will be thrown.
        # Catches the exception and displays error message then redirects the user.
        try:
            new_movie = "INSERT INTO movies (title, rating, info, user_id) VALUES (?, ?, ?, ?)"
            cursor.execute(new_movie, (movie_title, movie_rating, movie_info, user_id))
            connection.commit()
            success_message = "Added movie."
            return redirect(url_for("movies") + "?success_message=" + success_message)

        except sqlite3.IntegrityError:
            error_message = "Title already exists."
            return redirect(url_for("movies") + "?error_message=" + error_message)
    else:
        error_message = "Fill in both title and rating."
        return redirect(url_for("movies") + "?error_message=" + error_message)


# Gets userid then removes movie tied to userid.
@app.route("/remove_movie/<movie>", methods=["GET"])
def remove_movies(movie):
    userid = session["userid"]
    cursor.execute("DELETE FROM movies WHERE user_id=? AND title=?", (userid, movie))
    connection.commit()
    return redirect(url_for("movies"))


# Gets userid and clicked movie title. Loops through the user movie list and breaks when the clicked movie equals the
# movie in the list. Saves info and rating in new variables then renders description page with title, info and rating.
@app.route("/description", methods=["GET"])
def description():
    movie_list = get_movies(session["userid"])
    movie_name = request.args.get("movie")
    info = None
    rating = None

    for i in movie_list:
        if i["title"] == movie_name:
            info = i["info"]
            rating = i["rating"]
            break

    return render_template("description.html", title=movie_name, info=info, rating=rating)


# Gets user input. Calls database for user and checks if password equals the hashed password in the database.
# If success then login else display error message.
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    cursor.execute("SELECT password FROM users WHERE user_name=?", (username,))
    db_password = cursor.fetchone()
    if db_password is not None:
        hashed_password = db_password[0]
        is_valid = bcrypt.check_password_hash(hashed_password, password)
        if is_valid:
            cursor.execute("SELECT * FROM users WHERE user_name=? and password=?", (username, hashed_password))
            existing_user = cursor.fetchone()
            if existing_user is not None:
                session["userid"] = existing_user[0]
                return redirect(url_for("movies"))
        else:
            error_message = "Wrong password."
            return render_template("welcome.html", error_message=error_message)
    else:
        error_message = "User does not exist."
        return render_template("welcome.html", error_message=error_message)


# Renders welcome page.
@app.route("/logout", methods=["GET"])
def logout():
    return render_template("welcome.html")


# Renders register page.
@app.route("/register_page", methods=["GET"])
def register_page():
    return render_template("register.html")


# Gets username and password. Checks with database if user exists. If not a new user is created with a hashed password
# else display error message.
@app.route("/register_user", methods=["POST"])
def register():
    username = request.form["username"]

    if not username.isalnum():
        error_message = "Invalid username."
        return render_template("register.html", error_message=error_message)
    password = request.form["password"]

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = "INSERT INTO users (user_name, password) VALUES (?, ?)"
        cursor.execute(new_user, (username, hashed_password))
        connection.commit()
        success_message = "Registration successful"
        error_message = None
    except sqlite3.IntegrityError:
        error_message = "Username already exists."
        success_message = None

    if success_message:
        return render_template("welcome.html", success_message=success_message)
    else:
        return render_template("register.html", error_message=error_message)


# Runs application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

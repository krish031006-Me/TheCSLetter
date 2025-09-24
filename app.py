# Importing all the necessary modules
from flask import Flask, render_template, request, session, redirect, flash, url_for    
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from cs50 import SQL
import re
from helpers import login_required
from topics import categories
import json
from generate import newsletter
from apscheduler.schedulers.background import BackgroundScheduler
import random
from bs4 import BeautifulSoup
from datetime import datetime

"""# function to call newsletter-
def scheduled_call():
    # calling the trigger route to begin the newsletter creation
    try:
        url = "http://127.0.0.1:5000/trigger?token=a-very-secret-key"
        trigger = requests.get(url)
        print("Successfully called trigger route")
        print("Response body:", trigger.text)
    except Exception as e:
        print("Error in the background calling", e)

# scheduling the call
scheduler = BackgroundScheduler() # creating an instance
scheduler.add_job(scheduled_call, 'cron', hour = 20, minute=3) # everyday at 10 AM"""

# creating a flask app instance
app = Flask(__name__)
app.secret_key = "a-very-secret-key"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.debug = True  # make sure debug is enabled

# setting up sessions-
# not storing them permanently
app.config["SESSION_PERMANENT"] = False
# storing them in filesystem 
app.config["SESSION_TYPE"] = "filesystem"
# initialising app for use
Session(app)

# SQL datatbase
db = SQL("sqlite:///users.db")

# checking for response
@app.after_request 
def after_request(response): # response is a built in parameter which stores the response of server after the browser.
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache" # it doesn't allows to store dynamic cache.
    return response

# login route-
@app.route("/login", methods = ["GET","POST"])
def login():
    # checking the methods
    if request.method == "GET":
        return render_template("login.html")
    else:
        # getting the username and password
        username, password, email = (request.form.get("username")).lower().strip(), request.form.get("password").strip(), (request.form.get("email")).lower().strip()
        # whole details of thr userbase
        details = db.execute("SELECT * FROM users")
        # checking if the list is empty or not
        if details == []:
            flash("User doesn't exist, please register yourself.")
            return redirect("/register")
        # cheking if the user exists or not
        if not all([username, password, email]):
            flash("One or more fields were not entered.")
            return redirect("/login")
        # checking if the email is correct or not
        if email not in [(row["email"]).lower() for row in details]:
            flash("Entered email is wrong.")
            return redirect("/login")
        # using regex to check for correct email syntax
        match = re.match(r"^[\w!#$%&'\*\+-/=\?\^_`{|}~|]+@[A-Za-z0-9-]{1,63}\..+", email)
        if match == None:
            flash("Entered email is not valid.")
            return redirect("/login")
        
        # if the user exists-
        else:
            # getting the whole row info
            user_row = db.execute("SELECT * FROM users WHERE lower(email) = ?", email)
            # now we check if the password entered was correct or not
            if not check_password_hash(user_row[0]["hash"], password):
                flash("Entered password is incorrect.")
                return redirect("/login")
            # check if username is correct
            if (user_row[0]["username"]).lower() != username:
                flash("The entered username or email is incorrect")
                return redirect("/login")
            # if the username and password both are present-
            else:
                # updating the session a global dict for the id of user
                session["user_id"] = user_row[0]["id"]
                #redirecting to the homepage or dashboard
                flash("Logged in successfully.")
                return redirect("/")

# route for registering into the web application-
@app.route("/register", methods = ["POST","GET"])
def register():
    # checking for method
    if request.method == "GET":
        return render_template("register.html")
    else:
        # getting all the usernames 
        details = db.execute("SELECT * FROM users")
        # getting the details filled
        username, password, email = (request.form.get("username")).lower().strip(), request.form.get("password").strip(), (request.form.get("email")).lower().strip()
        # checking if all the fields were filled or not
        if not all([username, password, email]):
            # flashing a little alert before redirecting
            flash("One or more fields were not entered.")
            return redirect("/register")
        # checking if the email is unique or not
        if email in [(row["email"]).lower() for row in details]:
            flash("Entered email is already in use.")
            return redirect("/register")
        # using regex to check for correct email syntax
        match = re.match(r"^[\w!#$%&'\*\+-/=\?\^_`{|}~|]+@[A-Za-z0-9-]{1,63}\..+", email)
        if match == None:
            flash("Entered email is not valid.")
            return redirect("/register")
        else:
            # adding the user in the database and redirecting 
            try:
                db.execute("INSERT INTO users (username, hash, email) VALUES(?,?,?)", username.lower(), generate_password_hash(password), email)
            except ValueError:
                flash("Email is already in use.")
                return redirect("/register")
            user_id = db.execute("SELECT id FROM users WHERE lower(email) = ?", email)
            session["user_id"] = user_id[0]["id"]
            flash("Registered successfully.")
            return redirect("/")

# route for logging out-
@app.route("/logout")
def logout():
        # forgetting the old id
        session.clear()
        # redirecting 
        return redirect("/login")

# This is the main route or the route for the dashboard
@app.route("/", methods = ["GET", "POST"])
def dashboard():
    # getting all the details of the newsletter
    letter_details = db.execute("SELECT * FROM letters ORDER BY RANDOM() LIMIT 6")
    # also getting the lengthS
    length = len(letter_details)
    len_list = []
    while length > 0:
        len_list.append(length)
        length -= 1
    len_list.reverse()
    # checking the method of the route is get or post
    if request.method == "GET":
        # checking if details are None
        if not letter_details :
            return render_template("dashboard.html")
        # returning the template
        else:
            # striping HTML
            few_lines = []
            for element in letter_details:
                text = BeautifulSoup(element["content"], "html.parser").get_text()
                # find where is the emoji in text
                index = text.index('😊')
                few_lines.append(text[index+2:200])
            return render_template("dashboard.html", details = letter_details, length = len_list, lines = few_lines)
    # when method is post
    else:
        # check if the user has logged in or not
        if "user_id" not in session:
            flash("You need to log in first.", "error")
            return redirect("/login")
        # if the user is logged in and he clicks on one of the letters
        else:
            return redirect("/article")

# this is the route that will be used by both history template and dashboard template to show articles
@app.route("/article", methods = ["POST", "GET"])
@login_required
def show_article():
    # getting the letter_id user wants to know about
    letter_id, user_id = request.form.get("letter_id"), request.form.get("user_id")
    # fetching the details
    content = db.execute("SELECT * FROM letters WHERE user_id = ? AND letter_id = ?", user_id, letter_id)
    # rendering to the template-
    return render_template("article.html", letter = content[0])

''' this route is to generate the newsletter in testing phase only!
    You need to manually run it using /trigger in the url'''
@app.route("/trigger")
def trigger():
    # The main logic 
    users = db.execute("SELECT * FROM users WHERE status = 'subscribed'")
    if users == []:
        return redirect("/")
    if request.headers.get("Purpose") == "prefetch":
        print("Prefetch ignored")
        return "", 204
    print("Trigger called for real", request.method, request.path)
    for user in users:
        sessionId = user["id"]
        status = user["frequency"] 
        # getting the time-date for today
        try:
            today = datetime.today()
            weekday = today.weekday()
            letter = None # default value for letter
            # conditions for different frequencies-
            if status == "except_sundays":
                # if it's a sunday
                if weekday != 6:
                    # calling the newsletter function
                    letter = newsletter(sessionId)
                else:
                    pass
            elif status == "daily":
                letter = newsletter(sessionId)
            elif status == "weekly":
                # sending on monday
                if weekday == 0:
                    letter = newsletter(sessionId)
                else:
                    pass
            # trying to add the letter into the letters table-
            result = db.execute("SELECT COUNT(*) as count FROM letters WHERE user_id = ?", (sessionId,))

            length = result[0]["count"] if result else 0 # it will have zero in it if the user has no letter sended yet!

            if letter != None:
                db.execute("INSERT INTO letters (user_id, letter_id, title, content) VALUES(?, ?, ?, ?)", sessionId, length+1, letter["title"], letter["para"])
            
        except Exception as e:
            print("Error while executing newsletter on startup:", e)
    return redirect("/")

# route to subscribe to newsletter
@app.route("/subscribe", methods = ["GET", "POST"])
@login_required
def subscribe():
    # getting the details of the user
    try:
        details = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    except KeyError:
        flash("Sorry, you need to log In again", "error")
        return redirect("/login")
    # checking for different methods
    if request.method == "GET":
        if not details:
            flash("User not found please try again.", "error")
            return redirect("/login")
        # checking if the user is already subscribed or not
        status = db.execute("SELECT status FROM users WHERE id = ?", session["user_id"])
        if status[0]["status"] == "unsubscribed":
            return render_template("subscribe.html", details = details[0])
        else:
            categories = db.execute("SELECT categories FROM users WHERE id = ?", session["user_id"])
            # checking if categories exists or not
            if categories and categories[0]["categories"]:
                # storing a list there
                category_list = json.loads(categories[0]["categories"])  
            else:
                category_list = []
            frequency = db.execute("SELECT frequency FROM users WHERE id = ?", session["user_id"])
            return render_template("already_sub.html", categories = category_list, often = frequency[0]["frequency"])
    else:
        # getting the email entered
        email = (request.form.get("email_letter")).lower().strip()
        # using regex to check for correct email syntax
        match = re.match(r"^[\w!#$%&'\*\+-/=\?\^_`{|}~|]+@[A-Za-z0-9-]{1,63}\..+", email)
        if match == None:
            flash("Entered email is not valid.", "error")
            return redirect("/subscribe")
        # updating the table 
        db.execute("UPDATE users SET email = ? WHERE id = ?", email, session["user_id"])
        # redirecting
        return redirect("/categories")

# route for users who are subscribed
@app.route("/already", methods = ["GET"])
@login_required
def already():
    # checking for the methods
    if request.method == "GET":
        return redirect("/categories")

# route to check the stats
@app.route("/stats", methods =["GET"])
@login_required
def stats():
    count = db.execute("SELECT COUNT(username) AS total FROM users WHERE categories IS NOT NULL")
    if count and len(count) > 0:
        total = count[0]["total"] - 1
    else:
        total = 0
    return render_template("stats.html", count = total)

# to get the history of newsletters sended to you
@app.route("/history", methods = ["GET", "POST"])
@login_required
def history():
    # getting all the letters sent to the user
    letters = db.execute("SELECT * FROM letters WHERE user_id = ? ORDER BY sent_date DESC LIMIT 20", session["user_id"])
    if letters == None:
        return render_template("history.html")
    # for get method
    if request.method == "GET":
        few_lines = []
        for element in letters:
            text = BeautifulSoup(element["content"], "html.parser").get_text()
            index = text.find('😊')
            few_lines.append(text[index + 2: 200])
        return render_template("history.html", details = letters, lines = few_lines)
    # for post method
    else:
        # check if the user has logged in or not
        if "user_id" not in session:
            flash("You need to log in first.", "error")
            return redirect("/login")
        # if the user is logged in and he clicks on one of the letters
        else:
            return redirect(url_for("article", letters = letters))

# a route for the categories after they have been choosen
@app.route("/categories", methods = ["POST", "GET"])
@login_required
def show_categories():
    # checking for methods- 
    if request.method == "POST":
    # we wanna store the categories choosen by the user        
        choosen = request.form.getlist("category") # getlist will get all the checked values as a list
        # if choosen is an empty list i.e nothing filled by the user
        if choosen == []:
            return redirect("/skip")
        # if choosen categories are less than 6
        if len(choosen) < 6:
            # storing the key of the categories list of dicts
            dict_keys = [list(row.keys())[0] for row in categories]
            keys = [k for k in dict_keys if k not in choosen]
            # choosing random categories then
            # how many to choose
            to_choose = 6 - len(choosen)
            # choosing random categories
            to_append = random.sample(keys, to_choose)
            # appending them to choosen
            choosen.extend(to_append)
        # converting list into json
        choosen = json.dumps(choosen)
        # store the categories in the database and change their status
        db.execute("UPDATE users SET categories = ?, status = 'subscribed' WHERE id = ?", choosen, session["user_id"])
        # rendering a success template
        return redirect("/frequency")
    # if method is get
    else:
        return render_template("categories.html", categories = categories)
    
# a route for skipping the choose categories option
@app.route("/skip", methods = ["GET"])
@login_required
def skip():    
    # the default list for lazy people
    default = ["Web Development", "Systems", "CyberSecurity", "Software Engineering", "Competitive Programming", "Data Science & AI"]
    default = json.dumps(default)
    # storing the default in the database
    db.execute("UPDATE users SET categories = ?, status = 'subscribed' WHERE id = ?", default, session["user_id"])
    # rendering the sccess template
    flash("Categories selected!")
    return redirect("/frequency")

# a route for frequency
@app.route("/frequency", methods = ["POST", "GET"])
@login_required
def frequency():
    # checking for the methods
    if request.method == "GET":
        return render_template("frequency.html")
    else:
        # getting the frequency choosen by user
        status = request.form.get("frequency").strip()
        # updating it in the database
        db.execute("UPDATE users SET frequency = ? WHERE id = ?", status, session["user_id"])
        # redirecting 
        return render_template("subscribed.html")

# running in debug mode
if __name__ == "__main__":
    # only run the scheduler in the main process, not the reloader
    # scheduler.start()
    app.run(debug=True, use_reloader=True)
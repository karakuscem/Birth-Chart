import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, all_signs
from kerykeion import KrInstance, MakeSvgInstance, RelationshipScore
import datetime
import requests
import json

# APP OUTLINE
# REGISTER FUNCTION, LOGIN FUNCTION, SHOW USER BIRTHCHART, IF USER WANT TO STORE BIRTHCHART INFO SEND DATABASE, LOGOUT

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///charts.db")

@app.route("/")
@login_required
def index():
    user_name = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    return render_template("index.html", user_name=user_name)

@app.route("/login", methods=["GET", "POST"])
def login():
    #Forget user_id
    session.clear()
    #Show the page
    if request.method == "GET":
        return render_template("login.html")
    else:
        user_nickname = request.form.get("username")
        user_password = request.form.get("password")
        #Check correct usage.
        if not user_nickname:
            return apology("You must provide username")
        elif not user_password:
            return apology("You must provide password")
        #Query for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", user_nickname)
        
        #Check username and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], user_nickname):
            return apology("Invalid username and/or password")
        
        #Remember user
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If method GET show the page
    if request.method == "GET":
        return render_template("register.html")
    # If method POST check right usage and send data.
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("You must provide an username.")
        elif not password:
            return apology("You must provide a password.")
        elif not confirmation:
            return apology("Must provide confirmation.")
        elif confirmation != password:
            return apology("Confirmation must be the same with password.")
        elif len(username) < 4:
            return apology("Username must be contain at least four characters.")
        elif len(password) < 4:
            return apology("Password must be minimum four characters.")
        # Store password into hash
        hash = generate_password_hash(password,
        method='pbkdf2:sha256', salt_length=8)
        # Query to register user to database.
        try:
            user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
            username, hash)
            session["user_id"] = user
            return redirect("/")
        except ValueError:
            return apology("This username already taken.")

@app.route("/stored_data", methods=["GET", "POST"])
def store_data():
    """Show stored data"""
    if request.method == "GET":
        user_id = session["user_id"]
        user_data = db.execute("SELECT id, name, year, month, day, hour, minutes, birthplace, chart_type FROM stockedcharts WHERE user_id = ? ORDER BY id", user_id)
        return render_template("stored_data.html", user_data=user_data)

@app.route("/horoscopes", methods=["GET", "POST"])
def horoscopes():
    # If method GET show page
    if request.method == "GET":
        return render_template("/horoscopes.html")
    # If method POST show the selected page.
    else:
        # Check correct usage
        chart_style = request.form.get("chart")
        if chart_style == "Natal":
            return redirect("/natalchart")
        elif chart_style == "Composite":
            return redirect("/synastrychart")
        elif chart_style == "Transit":
            return redirect("/transitchart")
        else:
            return apology("You should select valid chart.")

@app.route("/natalchart", methods=["GET", "POST"])
def natalchart():
    # If method GET, show page.
    if request.method == "GET":
        return render_template("natalchart.html")
    else:
        # Variables to get data.
        user_id = session["user_id"]
        name = request.form.get("name")
        year = request.form.get("year")
        month = request.form.get("month")
        day = request.form.get("day")
        hour = request.form.get("hour")
        minutes = request.form.get("minute")
        birthplace = request.form.get("birthplace")
        # Check correct usage
        if not name or not year or not month or not day or not hour or not minutes or not birthplace:
            return apology("You must provide all information above")
        if int(year) < 0 or int(year) > datetime.datetime.today().year:
            return apology("You must provide valid year")
        if int(month) < 1 or int(month) > 12:
            return apology("You must provide valid month")
        if int(day) < 1 or int(day) > 31:
            return apology ("You must provide valid day")
        if int(hour) < 0 or int(hour) > 23:
            return apology("You must provide valid hour")
        if int(minutes) < 0 or int(minutes) > 59:
            return apology("You must provide valid minute")
        # Create new folder for user.
        path = (f"./static/{user_id}")
        if not os.path.exists(path):
            os.makedirs(path)
        # Calculate user's birth chart.
        first = KrInstance(name, int(year), int(month), int(day), int(hour), int(minutes), birthplace)
        calculate = MakeSvgInstance(first, chart_type="Natal", new_output_directory=path)
        # Save data if user want to.
        if request.form.get("save"):
            db.execute("INSERT INTO stockedcharts (user_id, name, year, month, day, hour, minutes, birthplace, chart_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       user_id, name, int(year), int(month), int(day), int(hour), int(minutes), birthplace, "Natal Chart")
        # Visualize birth chart
        calculate.makeSVG()
        natal_calculated = (f"{path}/{name}NatalChart.svg")
        # Daily horoscope and some infos about user's Sun sign
        person_sign = first.sun["sign"]
        params = (
        (f'sign', {all_signs[person_sign]}),
        ('day', 'today'),
        )
        request_info = requests.post('https://aztro.sameerkumar.website/', params=params)
        all_data = json.loads(request_info.text)
        description = all_data["description"]
        lucky_number = all_data["lucky_number"]
        compatibility = all_data["compatibility"]
        current_mood = all_data["mood"]
        return render_template("natal_horoscoped.html", natal_calculated=natal_calculated, description=description, lucky_number=lucky_number, compatibility=compatibility, current_mood=current_mood)
    
@app.route("/synastrychart", methods=["GET", "POST"])
def synastrychart():
    # If method GET, show page.
    if request.method == "GET":
        return render_template("synastrychart.html")
    else:
        # Variables to get data.
        user_id = session["user_id"]
        name = request.form.get("name")
        year = request.form.get("year")
        month = request.form.get("month")
        day = request.form.get("day")
        hour = request.form.get("hour")
        minutes = request.form.get("minute")
        birthplace = request.form.get("birthplace")
        second_name = request.form.get("second_name")
        second_year = request.form.get("second_year")
        second_month = request.form.get("second_month")
        second_day = request.form.get("second_day")
        second_hour = request.form.get("second_hour")
        second_minutes = request.form.get("second_minute")
        second_birthplace = request.form.get("second_birthplace")
        # Check correct usage
        if not name or not year or not month or not day or not hour or not minutes or not birthplace:
            return apology("You must provide all information above")
        if not second_name or not second_year or not second_month or not second_day or not second_hour or not second_minutes or not second_birthplace:
            return apology("You must provide all information above")
        if int(year) < 0 or int(year) > datetime.datetime.today().year and int(second_year) < 0 or int(second_year) > datetime.datetime.today().year:
            return apology("You must provide valid year")
        if int(month) < 1 or int(month) > 12 and int(second_month) < 1 or int(second_month) > 12:
            return apology("You must provide valid month")
        if int(day) < 1 or int(day) > 31 and int(second_day) < 1 or int(second_day) > 31:
            return apology ("You must provide valid day")
        if int(hour) < 0 or int(hour) > 23 and int(second_hour) < 0 or int(second_hour) > 23:
            return apology("You must provide valid hour")
        if int(minutes) < 0 or int(minutes) > 59 and int(second_minutes) < 0 or int(second_minutes) > 59:
            return apology("You must provide valid minute")
        # Create new folder for user.
        path = (f"./static/{user_id}")
        if not os.path.exists(path):
            os.makedirs(path)
        # Calculate birth chart.
        first = KrInstance(name, int(year), int(month), int(day), int(hour), int(minutes), birthplace)
        second = KrInstance(second_name, int(second_year), int(second_month), int(second_day), int(second_hour), int(second_minutes), second_birthplace)
        calculate = MakeSvgInstance(first, chart_type="Composite", second_obj=second, new_output_directory=path)
        # Visualize birth chart.
        calculate.makeSVG()
        synastry_calculated = (f"{path}/{name}CompositeChart.svg")
        # Calculate relationship score.
        relation_score = RelationshipScore(first, second_subject=second).score
        # Daily horoscope for both person.
        first_person_sign = first.sun["sign"]
        second_person_sign = second.sun["sign"]
        first_params = (
        (f'sign', {all_signs[first_person_sign]}),
        ('day', 'today'),
        )
        second_params = (
        (f'sign', {all_signs[second_person_sign]}),
        ('day', 'today'),
        )
        first_request_info = requests.post('https://aztro.sameerkumar.website/', params=first_params)
        second_request_info = requests.post('https://aztro.sameerkumar.website/', params=second_params)
        first_all_data = json.loads(first_request_info.text)
        second_all_data = json.loads(second_request_info.text)
        first_description = first_all_data["description"]
        first_lucky_number = first_all_data["lucky_number"]
        first_compatibility = first_all_data["compatibility"]
        first_current_mood = first_all_data["mood"]
        second_description = second_all_data["description"]
        second_lucky_number = second_all_data["lucky_number"]
        second_compatibility = second_all_data["compatibility"]
        second_current_mood = second_all_data["mood"]
        return render_template("synastry_horoscoped.html", synastry_calculated=synastry_calculated, relation_score=relation_score, name=name, second_name=second_name, first_description=first_description,
                               first_lucky_number=first_lucky_number, first_compatibility=first_compatibility, first_current_mood=first_current_mood,
                               second_description=second_description, second_lucky_number=second_lucky_number, second_compatibility=second_compatibility,second_current_mood=second_current_mood)
    
@app.route("/transitchart", methods=["GET", "POST"])
def transitchart():
    # If method GET, show page.
    if request.method == "GET":
        return render_template("transitchart.html")
    else:
        # Variables to get data.
        user_id = session["user_id"]
        name = request.form.get("name")
        year = request.form.get("year")
        month = request.form.get("month")
        day = request.form.get("day")
        hour = request.form.get("hour")
        minutes = request.form.get("minute")
        birthplace = request.form.get("birthplace")
        second_year = request.form.get("second_year")
        second_month = request.form.get("second_month")
        second_day = request.form.get("second_day")
        second_hour = request.form.get("second_hour")
        second_minutes = request.form.get("second_minute")
        second_place = request.form.get("place")
        # Check correct usage
        if not name or not year or not month or not day or not hour or not minutes or not birthplace:
            return apology("You must provide all information above")
        if not second_year or not second_month or not second_day or not second_hour or not second_minutes or not second_place:
            return apology("You must provide all information above")
        if int(year) < 0 or int(year) > datetime.datetime.today().year and int(second_year) < 0 or int(second_year) > datetime.datetime.today().year:
            return apology("You must provide valid year")
        if int(month) < 1 or int(month) > 12 and int(second_month) < 1 or int(second_month) > 12:
            return apology("You must provide valid month")
        if int(day) < 1 or int(day) > 31 and int(second_day) < 1 or int(second_day) > 31:
            return apology ("You must provide valid day")
        if int(hour) < 0 or int(hour) > 23 and int(second_hour) < 0 or int(second_hour) > 23:
            return apology("You must provide valid hour")
        if int(minutes) < 0 or int(minutes) > 59 and int(second_minutes) < 0 or int(second_minutes) > 59:
            return apology("You must provide valid minute")
        # Create folder for user
        path = (f"./static/{user_id}")
        if not os.path.exists(path):
            os.makedirs(path)
        # Calculate birth chart
        first = KrInstance(name, int(year), int(month), int(day), int(hour), int(minutes), birthplace)
        second = KrInstance("x", int(second_year), int(second_month), int(second_day), int(second_hour), int(second_minutes), second_place)
        calculate = MakeSvgInstance(first, chart_type="Transit", second_obj=second, new_output_directory=path)
        # Visualize birth chart
        calculate.makeSVG()
        transit_calculated = (f"{path}/{name}TransitChart.svg")
        return render_template("transit_horoscoped.html", transit_calculated=transit_calculated)

@app.route("/about", methods=["GET", "POST"])
def about():
    # Show page
    if request.method == "GET":
        return render_template("about.html")
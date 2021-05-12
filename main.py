import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import erro, login_required
import logging


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]

# Ensure responses aren't cached
@app.after_request
def after_request(response):
  response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
  response.headers["Expires"] = 0
  response.headers["Pragma"] = "no-cache"
  return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///client.db")


def inpt(field):
  """ input required """
  if not request.form.get(field):
    return flash(f"Must provide {field}!")
    
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
  """ Add new client  """

  if request.method == "POST":
    inpt_checks = inpt("clientname")
    if inpt_checks != None:
        return inpt_checks

    # save new client to db     
    try:
        db.execute("""
    INSERT INTO clients (user_id, clientname, email, mobile, aptsize, budget, move_date, w_or_e, up_down_town, pets, grantor, note)
    VALUES (:user_id, :clientname, :email, :mobile, :aptsize, :budget, :move_date, :w_or_e, :up_down_town, :pets, :grantor, :note)
    """,
    user_id=session["user_id"],
    clientname=request.form.get("clientname"),
    email=request.form.get("clientemail"),
    mobile=request.form.get("mobile"),
    aptsize=request.form.get("size"),
    budget=request.form.get("budget"),
    move_date=request.form.get("movedate"),
    w_or_e=request.form.get("area2"),
    up_down_town=request.form.get("area"),
    pets=request.form.get("pets"),
    grantor=request.form.get("grantor"),
    note= request.form.get("note")
    )
    except:
      return erro("Client name already exists")

    # notifications 
    flash("New client successfully added!")

    # Redirect user to index.html
    return redirect("/")
  else:
    return render_template("add.html")

@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
  """ Add new appointment"""

  if request.method == "POST":
    inpt_checks = inpt("clientname") and inpt("moble")
    if inpt_checks != None:
        return inpt_checks

    # Save new appointment to db
    clientdb = db.execute("""
    SELECT *
    FROM clients
    WHERE clientname = :clientname
    """, clientname = request.form.get("clientname"))

    # ensure clietn exist 
    for i in clientdb:
        if request.form.get("clientname") == i["clientname"] and request.form.get("mobile") == i["mobile"]:
          db.execute("""
          INSERT INTO appointments (user_id, clientname, email, mobile, aptsize, budget, move_date, w_or_e, up_down_town, pets, grantor, note, appt_date, modified)
          VALUES (:user_id, :clientname, :email, :mobile, :aptsize, :budget, :move_date, :w_or_e, :up_down_town, :pets, :grantor, :note, :appt_date, :modified)
          """,
          user_id=session["user_id"],
          email= i["email"],
          aptsize = i["aptsize"],
          budget = i["budget"],
          move_date = i["move_date"],
          w_or_e = i["w_or_e"],
          up_down_town = i["up_down_town"],
          pets = i["pets"],
          grantor = i["grantor"],
          note = i["note"],
          modified = i["modified"],
          appt_date = request.form.get("appt_datetime"),
          clientname= request.form.get("clientname"),
          mobile = request.form.get("mobile")
          )

          # notifications 
          flash("New appointment successfully added!")

          # redirect to confirmed appoinmetns page
          return redirect("/confirmed_appointments")
    else:   
      # if client not exist
      return erro("Client not found")
  else:
    return render_template("appointment.html")

@app.route("/confirmed_appointments")
@login_required
def confirmed_appointments():
  """Show all appointments"""

  # get all appointments from db
  appointments = db.execute("""
      SELECT *
      FROM appointments
      WHERE user_id = :user_id
      ORDER BY appt_date;
      """, user_id=session["user_id"])
  return render_template("confirmed_appointments.html", appointments=appointments)

@app.route("/")
@login_required
def index():
  """Show all clients"""

  # Get all clients from db
  clients = db.execute("""
      SELECT *
      FROM clients
      WHERE user_id = :user_id
      ORDER BY move_date;
      """, user_id=session["user_id"])
      
  # Get current time  
  return render_template("index.html", clients=clients)

@app.route("/history")
@login_required
def history():
  """Show history of deleted clients"""

  # Get deleted clients from db
  deletedclients = db.execute("""
      SELECT *
      FROM deleted_clients
      WHERE user_id = :user_id
      ORDER BY delete_date DESC;
  """, user_id=session["user_id"])
  return render_template("history.html", deletedclients=deletedclients)


@app.route("/login", methods=["GET", "POST"])
def login():
  """Log user in"""

  # Forget any user_id
  session.clear()

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    # Ensure username and password was submitted
    inpt_checks = inpt("username") or inpt("password")
    if inpt_checks is not None:
      return inpt_checks
      # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                        username=request.form.get("username"))

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
      # notifications 
      flash ("Invalid username or password!") 
      return render_template("login.html")
      # return erro("Invalid Username or Password")

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    flash("Welcome Back!")  
    # Redirect user to home page
    return redirect("/")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
      return render_template("login.html")


@app.route("/logout")
def logout():
  """Log user out"""

  # Forget any user_id
  session.clear()

  # Redirect user to login form
  return redirect("/")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
  """search client."""

  if request.method == "POST":
      inpt_checks = inpt("clientname") and inpt("mobile")
      if inpt_checks != None:
          return inpt_checks

      clientsdb = db.execute("""
          SELECT *
          FROM clients
          WHERE user_id = :user_id
          """, user_id=session["user_id"])

      for i in clientsdb:
          if i["clientname"].lower() == request.form.get("clientname").lower() or i["mobile"] == request.form.get("mobile"):

              flash("Client Found!")

              return render_template("found.html",
              clients=i["clientname"],
              email= i["email"],
              mobile=i["mobile"],
              aptsize=i["aptsize"],
              budget=i["budget"],
              movedate=i["move_date"],
              west_east=i["w_or_e"],
              up_town_town=i["up_down_town"],
              pets=i["pets"],
              grantor=i["grantor"],
              note=i["note"],
              add=i["modified"])
      else:
          return erro("Client not found")

  else:
      return render_template("search.html")

@app.route("/register", methods=["GET", "POST"])
def register():
  """Register user"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    inpt_checks = inpt("username") or inpt("password") or inpt("confirmation")
    if inpt_checks != None:
      return inpt_checks

    if request.form.get("username") == '' or request.form.get("password") == '':
      flash ("All fields are required. Try again!") 
      return redirect ("/register")

    if request.form.get("password") != request.form.get("confirmation"):
      flash ("Password not match!")
      return redirect ("/register")

    try:
      new_user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
              username=request.form.get("username"),
              hash=generate_password_hash(request.form.get("password")))
    except:
      return erro("Username already exists")

    if new_user is None:
        return erro("Registration erro")
        
    session["user_id"] = new_user

    # notification
    flash("You have successfully registered and logged in.")

    # Redirect user to index.html
    return redirect("/")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
      return render_template("register.html")


@app.route("/cancel_appts", methods=["GET", "POST"])
@login_required
def cancel_appts():
  """Cancel confirmed appoinments"""

  if request.method == "POST":

      clientsdb = db.execute("""
          SELECT *
          FROM appointments
          WHERE user_id=:user_id
          """,
          user_id=session["user_id"])

      for i in clientsdb:
          if request.form.get("clientname") == '':
              return erro("Must provide client's name")

          if request.form.get("clientname") == i["clientname"] or request.form.get("mobile") == i["mobile"]:

              db.execute("""
              INSERT INTO deleted_clients (user_id, clientname, email, mobile, aptsize, budget, move_date, w_or_e, up_down_town, pets, note, modified, appt_date, grantor)
              SELECT user_id, clientname, email, mobile, aptsize, budget, move_date, w_or_e, up_down_town, pets, note, modified, appt_date, grantor
              FROM appointments
              WHERE clientname = :clientname
              """, clientname = request.form.get("clientname"))

              db.execute("""
              DELETE FROM appointments
              WHERE clientname = :clientname
              """, clientname = request.form.get("clientname"))

              flash("Appointment has been successfully canceled!")

              return redirect("/confirmed_appointments")
      else:
          return erro("Client not found")

  else:
      return render_template("cancel_appts.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
  """delete client"""

  if request.method == "POST":

      clientsdb = db.execute("""
          SELECT *
          FROM clients
          WHERE user_id=:user_id
          """,
          user_id=session["user_id"])

      for i in clientsdb:
          if request.form.get("deletename")== '':
              return erro("Must provide client name")

          if request.form.get("deletename") == i["clientname"] or request.form.get("mobile") == i["mobile"]:
            db.execute("""
            INSERT INTO deleted_clients (user_id, clientname, email, mobile, aptsize, budget, move_date, w_or_e, up_down_town, pets, note, modified, grantor)
            SELECT user_id, clientname, email, mobile, aptsize, budget, move_date, w_or_e, up_down_town, pets, note, modified, grantor
            FROM clients
            WHERE clientname = :clientname
            """, clientname = request.form.get("deletename"))
            db.execute("""
            DELETE FROM clients
            WHERE clientname = :clientname
            """, clientname = request.form.get("deletename"))
            flash("Client has been successfully deleted!")
            return redirect("/")
      else:
        return erro("Client not found")
  else:
    return render_template("delete.html")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():

  if request.method == "POST":
    inpt_checks = inpt("clientname")
    if inpt_checks != None:
            return inpt_checks
    clientname = request.form.get("clientname")
    email = request.form.get("clientemail")
    mobile = request.form.get("mobile")
    aptsize = request.form.get("size")
    budget = request.form.get("budget")
    move_date = request.form.get("movedate")
    w_or_e = request.form.get("area2")
    up_down_town = request.form.get("area")
    pets = request.form.get("pets")
    grantor = request.form.get("grantor")
    note = request.form.get("note")

    clientsdb = db.execute("""
    SELECT *
    FROM clients
    WHERE user_id = :user_id
    """, user_id=session["user_id"])


    for i in clientsdb:

        if email == '':
            email = i["email"]

        if mobile == '':
            mobile = i["mobile"]

        if aptsize == '':
            aptsize = i["aptsize"]

        if budget == '':
            budget = i["budget"]

        if move_date == '':
            move_date = i["move_date"]

        if w_or_e == '':
            w_or_e = i["w_or_e"]

        if up_down_town == '':
            up_down_town = i["up_down_town"]

        if pets == '':
            pets = i["pets"]

        if grantor == '':
            grantor = i["grantor"]

        if note == '':
            note = i["note"]

        if clientname == i["clientname"]:
          db.execute("""
          UPDATE clients
          SET clientname=:clientname, 
          email=:email, 
          mobile=:mobile, 
          aptsize=:aptsize, 
          budget=:budget, 
          move_date=:move_date, 
          w_or_e=:w_or_e, 
          up_down_town=:up_down_town, 
          pets=:pets, 
          grantor=:grantor, 
          note=:note
          WHERE clientname =:clientname""",
          clientname=clientname,
          email=email,
          mobile=mobile,
          aptsize=aptsize,
          move_date=move_date,
          budget=budget,
          w_or_e=w_or_e,
          up_down_town=up_down_town,
          pets=pets,
          grantor=grantor,
          note=note)

          # Alert bar display Cash Added!
          flash("Client Information has been successfully updated!")

          return redirect("/")

    else:
      return erro("Client not found")
  else:
    return render_template("update.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return erro(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

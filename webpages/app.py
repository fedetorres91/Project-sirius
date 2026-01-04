import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session.get("user_id")
    if not user_id:
        redirect("/login")

    # create table of shares and
    db.execute("CREATE TABLE IF NOT EXISTS shares (user_id INT, symbol TEXT, price REAL, qty INTEGER, mkt_value REAL, cost_basis REAL, PRIMARY KEY (user_id, symbol));")
    user_stocks = db.execute("SELECT * FROM shares WHERE user_id = ?", user_id)
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    cash = float(user["cash"])
    total = cash
    if user_stocks:
        for stock in user_stocks:
            total = total + stock["mkt_value"]
            symbol = stock["symbol"]
            price = lookup(symbol)["price"]
            mkt_value = price*stock["qty"]
            db.execute("UPDATE shares SET price = ?, mkt_value = ? WHERE user_id = ? AND symbol = ?",
                       price, mkt_value, user_id, symbol)

    return render_template("index.html", cash=cash, user_stocks=user_stocks, total=total, usd=usd)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")

        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # user reached via post as submitting register form
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # cheeck if valid username

        if not username:
            return apology("Please provide a valid username")
        if not password:
            return apology("Please provide a valid password")
        if not confirmation:
            return apology("Please confirm password")
        if password != confirmation:
            return apology("password does not coincide")

        # try to  add username and password to finance.db if username doesnt exists"""

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username,
                       generate_password_hash(password))
        except:
            return apology("username already exists. Please provide another username")

        # Redirect user to home page
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        # user reached via get as not registered yet
        return render_template("register.html")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    """Change password"""
    if request.method == "GET":
        return render_template("change_password.html")

    else:

        # Ensure password was submitted
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        if not current_password:
            return apology("must provide current password", 403)

        elif not new_password:
            return apology("must provide new password", 403)

        elif not confirmation:
            return apology("must confirm new password", 403)

        elif confirmation != new_password:
            return apology("password confirmation does not match", 403)
        else:
            user_id = session.get("user_id")

            # Query database for username
            rows = db.execute(
                "SELECT * FROM users WHERE id = ?", user_id)

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                    rows[0]["hash"], current_password):
                return apology("invalid password", 403)
            else:
                db.execute("UPDATE users SET hash=? WHERE id ==?",
                           generate_password_hash(new_password), user_id)

        flash("Password has been updated")

        # Redirect user to home page
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

from datetime import datetime
import sys
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
ADMIN = "admin123"


# Function to perform SQL queries
def execute(query, *values, fetchall=False):
    conn = sqlite3.connect('bookStore.db')
    cursor = conn.cursor()

    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)

    if fetchall:
        list_of_dicts = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
        result = list_of_dicts
    else:
        result = None

    conn.commit()
    conn.close()
    return result


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show books of store"""

    if "person_id" not in session:
        return redirect("/login")
    books = execute("SELECT title, author FROM books WHERE on_loan = ? ", 0,fetchall=True)

    books_on_loan = execute("SELECT title, author FROM books WHERE on_loan = ? AND loanee = ?",1,session["person_id"],fetchall=True)
    return render_template("index.html",books=books,books_on_loan=books_on_loan)


@app.route("/admin")
def admin_index():
    books = execute("SELECT title, author, genre, price, loanee, on_loan FROM books",fetchall=True)
    people = execute("SELECT card_number, firstname, lastname, email, address FROM people",fetchall=True)
    loans = execute("SELECT title, loanee, year, month, day FROM loans",fetchall=True)
    return render_template("admin_index.html",books=books,people=people,loans=loans)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """ADD BOOKS"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        price = request.form.get("price")
        genre = request.form.get("genre")

        if not title or not author or not price or not genre:
            return render_template("/apology.html",error="Invalid Title or Author or Price or Genre")
        price = float(price)
        if price <= 0:
            return render_template("/apology.html",error="Wrong Price")

        execute("INSERT INTO books (title,author,price,genre) VALUES(?,?,?,?)", title, author, price, genre)

        # Redirect user to home page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add_book.html")


@app.route("/delete_book", methods=["GET", "POST"])
def delete_book():
    if request.method == "GET":
        books = execute("SELECT title FROM books", fetchall=True)
        return render_template("del_book.html",books=books)
    else:
        title = request.form.get("title")
        if title:
            execute("DELETE FROM books WHERE title = ?",title)
        return redirect("/admin")


@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
    if request.method == "GET":
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day
        text = "SELECT loanee FROM books WHERE on_loan = ?"
        loanees = execute("SELECT loanee FROM loans WHERE year > ? OR month > ? OR day+? > ?",year,month,day,7, fetchall=True)
        return render_template("del_user.html",loaness=loanees)
    else:
        person_id = request.form.get("person_id")
        if person_id:
            execute("DELETE FROM people WHERE card_number = ?",person_id)
        return redirect("/admin")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if request.form.get("A_password") == ADMIN:
            return redirect("/admin")

        # Ensure username was submitted
        if not request.form.get("card_number"):
            return render_template("apology.html", error="must provide card_number")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("apology.html", error="must provide password")

        rows = execute("SELECT * FROM people WHERE card_number = ?", request.form.get("card_number"),fetchall=True)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", error="invalid username and/or password")
        # Ensure card_number exists and password is correct

        # Remember which user has logged in
        session["person_id"] = rows[0]["card_number"]

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
    if request.method == "GET":
        return render_template("register.html")
    else:
        card_number = request.form.get("card_number")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        if not card_number:
            return render_template("apology.html", error="Please enter a card_number")
        if not password:
            return render_template("apology.html", error="Please enter a password")
        if not confirmation:
            return render_template("apology.html", error="Please enter a confirmation")
        if password != confirmation:
            return render_template("apology.html", error="password mismatch")
        if not password.isalnum() or len(password) < 7:
            return render_template("apology.html", error="Weak password")

        hash_password = generate_password_hash(password)
        try:
            execute("INSERT INTO people (card_number,firstname,lastname,hash,email,address) VALUES(?, ?, ?, ?, ?, ?)",card_number, firstname, lastname, hash_password, email,address)
        except:
            return render_template("apology.html", error=sys.exc_info())

        new_user = execute("SELECT * FROM people WHERE card_number = ?",card_number,fetchall=True)
        session["person_id"] = new_user[0]["card_number"]
        return redirect("/")


@app.route("/loan",methods=["GET", "POST"])
def loan():
    if request.method == "POST":
        book = request.form.get("book")
        person_id = session["person_id"]
        if book:
            book_ids = execute("SELECT book_id FROM books WHERE title = ?",book,fetchall=True)
            book_id = book_ids[0]["book_id"]
            today = datetime.now()
            year = today.year
            month = today.month
            day = today.day
            execute("INSERT INTO loans (book_id, title, loanee, year, month, day) VALUES (?,?,?,?,?,?)",book_id,book,person_id,year,month,day)
            execute("UPDATE books SET on_loan = ?, loanee = ? WHERE title = ?", 1, person_id, book)
            flash("Book loaned successfully. Please return it within the next 7 days")
        return redirect("/")
    else:
        person_id = session["person_id"]
        row = execute("SELECT book_id FROM books WHERE loanee = ?", person_id, fetchall=True)
        if len(row) == 1:
            flash("Already have a book on loan")
            return redirect("/")
        books = execute("SELECT title FROM books WHERE on_loan = ?", 0,fetchall=True)
        return render_template("loan.html",books=books)


@app.route("/returning", methods=["GET", "POST"])
def returning():
    if request.method == "POST":
        book = request.form.get("book")
        person_id = session["person_id"]
        if book:
            execute("UPDATE books SET on_loan = ?, loanee = ? WHERE title = ?",0,None,book)
            flash("Book returned successfully")
        return redirect("/")
    else:
        person_id = session["person_id"]
        loaned_books = execute("SELECT title FROM books WHERE on_loan = ? AND loanee = ?",1,person_id,fetchall=True)
        return render_template("return.html",loaned_books=loaned_books)

if __name__ == '__main__':
    app.run(debug=True)
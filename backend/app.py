from flask import Flask, render_template, request, redirect, session
from database import get_db_connection

app = Flask(__name__)
app.secret_key = "campus_secret"

@app.route("/")
def index():
    search = request.args.get("search")
    category = request.args.get("category")
    max_price = request.args.get("price")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM items WHERE 1=1"
    values = []

    if search:
        query += " AND item_name LIKE %s"
        values.append(f"%{search}%")

    if category:
        query += " AND category = %s"
        values.append(category)

    if max_price:
        query += " AND price <= %s"
        values.append(max_price)

    cursor.execute(query, values)
    items = cursor.fetchall()

    return render_template("index.html", items=items)


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
            (request.form["name"], request.form["email"], request.form["password"])
        )
        db.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (request.form["email"], request.form["password"])
        )
        user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/add_item", methods=["GET","POST"])
def add_item():
    if request.method == "POST":
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO items (user_id,item_name,price,category,condition_item,description) VALUES (%s,%s,%s,%s,%s,%s)",
            (session["user_id"], request.form["item_name"], request.form["price"],
             request.form["category"], request.form["condition"], request.form["description"])
        )
        db.commit()
        return redirect("/")
    return render_template("add_item.html")

app.run(debug=True)

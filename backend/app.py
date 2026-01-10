from flask import Flask, render_template, request, redirect, session
from database import get_db_connection
from flask import flash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "backend/static/uploads"
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect("/register")

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "danger")
            return redirect("/register")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This email is already registered. Please login.", "warning")
            return redirect("/login")

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()

        flash("Registration successful! Please login to continue.", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            flash("Login successful. Welcome to Campus Marketplace!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")



@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        category = request.form["category"]
        condition_item = request.form["condition"]
        price = request.form["price"]

        image_file = request.files.get("image")
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO items
            (user_id, item_name, description, category, condition_item, price, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session["user_id"],
            item_name,
            description,
            category,
            condition_item,
            price,
            filename
        ))

        db.commit()
        return redirect("/profile")

    return render_template("add_item.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # ---------- UPDATE PROFILE ----------
    if request.method == "POST":
        phone = request.form.get("phone")
        department = request.form.get("department")
        semester = request.form.get("semester")

        profile_pic = request.files.get("profile_pic")
        filename = None

        if profile_pic and profile_pic.filename != "":
            filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        if filename:
            cursor.execute("""
                UPDATE users
                SET phone=%s, department=%s, semester=%s, profile_pic=%s
                WHERE id=%s
            """, (phone, department, semester, filename, session["user_id"]))
        else:
            cursor.execute("""
                UPDATE users
                SET phone=%s, department=%s, semester=%s
                WHERE id=%s
            """, (phone, department, semester, session["user_id"]))

        db.commit()
        return redirect("/profile")

    # ---------- FETCH USER DETAILS ----------
    cursor.execute("""
    SELECT id, item_name, category, price, condition_item, description, image
    FROM items
    WHERE user_id=%s
""", (session["user_id"],))

    user = cursor.fetchone()

    # ---------- FETCH USER'S POSTED ITEMS ----------
    cursor.execute("""
        SELECT item_name, category, price, condition_item, description,image
        FROM items
        WHERE user_id=%s
    """, (session["user_id"],))
    my_items = cursor.fetchall()

    return render_template("profile.html", user=user, my_items=my_items)


@app.route("/items")
def browse_items():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    search = request.args.get("search")
    category = request.args.get("category")
    price = request.args.get("price")

    query = "SELECT * FROM items WHERE 1=1"
    values = []

    if search:
        query += " AND item_name LIKE %s"
        values.append(f"%{search}%")

    if category:
        query += " AND category = %s"
        values.append(category)

    if price:
        query += " AND price <= %s"
        values.append(price)

    cursor.execute(query, values)
    items = cursor.fetchall()

    return render_template("items.html", items=items)


@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        category = request.form["category"]
        condition_item = request.form["condition"]
        price = request.form["price"]

        cursor.execute("""
            UPDATE items
            SET item_name=%s, description=%s, category=%s,
                condition_item=%s, price=%s
            WHERE id=%s AND user_id=%s
        """, (
            item_name,
            description,
            category,
            condition_item,
            price,
            item_id,
            session["user_id"]
        ))

        db.commit()
        return redirect("/profile")

    cursor.execute("""
        SELECT * FROM items
        WHERE id=%s AND user_id=%s
    """, (item_id, session["user_id"]))
    item = cursor.fetchone()

    if not item:
        flash("Item not found or unauthorized access.", "danger")
        return redirect("/profile")

    return render_template("edit_item.html", item=item)

@app.route("/delete_item/<int:item_id>")
def delete_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM items
        WHERE id=%s AND user_id=%s
    """, (item_id, session["user_id"]))

    db.commit()
    return redirect("/profile")


app.run(debug=True)

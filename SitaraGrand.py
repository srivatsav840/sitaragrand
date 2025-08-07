import os
import psycopg2
from psycopg2 import OperationalError
from flask import Flask, render_template, redirect, url_for, request, abort, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'srivatsav'
UPLOAD_FOLDER = 'static/images'  # You can choose any subfolder inside static
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/sitaraadmin", methods=["GET", "POST"])
def sitaraadmin():
    if request.method == "POST":
        category = request.form.get("category")
        item_name = request.form.get("itemname")
        price = request.form.get("price")

        file = request.files.get("itemimage")
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            os.makedirs(save_path, exist_ok=True)
            file.save(os.path.join(save_path, filename))
        elif file and file.filename != '':
            flash("Invalid image file type.", "error")

        if not category or not item_name or not price:
            flash("Category, Item Name, and Price are required.", "error")
            return render_template("sitaraadmin.html", categories=menucard)

        try:
            price_int = int(price)
        except ValueError:
            flash("Price must be a valid number.", "error")
            return render_template("sitaraadmin.html", categories=menucard)

        try:
            # Check if item exists
            check_query = "SELECT COUNT(*) FROM menu WHERE category = %s AND items = %s"
            mycursor.execute(check_query, (category, item_name))
            (count,) = mycursor.fetchone()

            if count > 0:
                flash(f"Item '{item_name}' already exists in category '{category}'.", "warning")
                return render_template("sitaraadmin.html", categories=menucard)

            insert_query = "INSERT INTO menu (category, items, price, itemimage) VALUES (%s, %s, %s, %s)"
            mycursor.execute(insert_query, (category, item_name, price_int, filename))
            mydb.commit()
            flash(f"Menu item '{item_name}' added successfully!", "success")

        except Exception as e:
            flash(f"Database error: {e}", "error")

    return render_template("sitaraadmin.html", categories=menucard)




try:
    mydb = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
        )
    mycursor = mydb.cursor()
except OperationalError as e:
    mydb = None
    mycursor = None
    print(f"Error connecting to PostgreSQL database: {e}")


menucard = [
    "Biryani Item",
    "Egg Starters",
    "Chicken Starters",
    "Mutton Starters",
    "Prawns & Fish Starters",
    "Fish Starters",
    "Prawn Starters",
    "Tandoori Starters",
    "Noodles",
    "Ice Creams",
    "Veg Curry Items",
    "Mutton Currys",
    "Fish Currys",
    "Veg Soups",
    "Non-Veg Soups",
    "Chinese Starters",
    "Others"
]

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/menu", methods=["GET"])
def menu():

    return render_template("menu.html", categories=menucard)


@app.route("/menu/<category_name>")
def menu_items(category_name):
    if mycursor is None:
        return "Database connection error. Please try again later."

    try:
        # Validate category_name is in menucard list
        if category_name not in menucard:
            abort(404, description=f"Category '{category_name}' not found.")

        # Use parameterized query properly
        query = "SELECT items, price, itemimage FROM menu WHERE category = %s"
        mycursor.execute(query, (category_name,))

        # Fetch all rows; each row = (item_name, price, image_filename)
        items = mycursor.fetchall()

    except Exception as e:
        return f"Error fetching menu items: {e}"

    return render_template("items.html", category_name=category_name, items=items)




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_from_directory,
    jsonify
)

import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename


# =========================================================
# OPTIONAL YOLO IMPORT
# =========================================================

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    YOLO_AVAILABLE = False
    YOLO_ERROR = str(e)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "kabadiwala_connect_secret_key"


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE = os.path.join(
    BASE_DIR,
    "kabadiwala.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# FAIR PRICE RATES
# Demo/reference rates only
# =========================================================

FAIR_PRICE_RATES = {

    "Paper": 15,

    "Cardboard": 12,

    "Books": 20,

    "Plastic": 25,

    "Metal": 40,

    "Glass": 8,

    "E-Waste": 80
}


# =========================================================
# YOLO MODEL
# =========================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "yolov8n.pt"
)

model = None

if YOLO_AVAILABLE:

    try:

        model = YOLO(MODEL_PATH)

        print(
            "======================================"
        )

        print(
            "AI MODEL LOADED SUCCESSFULLY!"
        )

        print(
            "MODEL:",
            MODEL_PATH
        )

        print(
            "======================================"
        )

    except Exception as e:

        model = None

        print(
            "======================================"
        )

        print(
            "AI MODEL COULD NOT BE LOADED"
        )

        print(
            "MODEL:",
            MODEL_PATH
        )

        print(
            "ERROR:",
            e
        )

        print(
            "======================================"

        )

else:

    print(
        "Ultralytics could not be imported."
    )

    print(
        "YOLO ERROR:",
        YOLO_ERROR
    )


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = sqlite3.connect(
        DATABASE,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA busy_timeout = 30000"
    )

    return connection


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()


        # Validation

        if (
            not name
            or not mobile
            or not location
            or not password
            or not role
        ):

            return render_template(
                "register.html",
                error="Please fill all fields."
            )


        # Check role

        if role not in [
            "user",
            "collector",
            "recycler"
        ]:

            return render_template(
                "register.html",
                error="Please select a valid role."
            )


        connection = get_db_connection()


        try:

            connection.execute(
                """
                INSERT INTO users
                (
                    name,
                    mobile,
                    location,
                    password,
                    role
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    mobile,
                    location,
                    password,
                    role
                )
            )

            connection.commit()

            connection.close()


            return render_template(
                "register.html",
                success="Registration successful! Please login."
            )


        except sqlite3.IntegrityError:

            connection.close()

            return render_template(
                "register.html",
                error="Mobile number already registered."
            )


        except Exception as e:

            connection.close()

            return render_template(
                "register.html",
                error="Registration failed: " + str(e)
            )


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()


        connection = get_db_connection()


        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE mobile = ?
            AND password = ?
            AND role = ?
            """,
            (
                mobile,
                password,
                role
            )
        ).fetchone()


        connection.close()


        if user:

            session.clear()

            session["user_id"] = user["id"]

            session["name"] = user["name"]

            session["mobile"] = user["mobile"]

            session["location"] = user["location"]

            session["role"] = user["role"]


            if role == "user":

                return redirect(
                    "/customer_dashboard"
                )


            elif role == "collector":

                return redirect(
                    "/dashboard"
                )


            elif role == "recycler":

                return redirect(
                    "/recycler"
                )


        return render_template(
            "login.html",
            error="Invalid mobile number, password or role."
        )


    return render_template(
        "login.html"
    )


# =========================================================
# CUSTOMER DASHBOARD
# =========================================================

@app.route(
    "/customer_dashboard"
)
def customer_dashboard():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "user":

        return redirect("/login")


    connection = get_db_connection()


    requests_data = connection.execute(
        """
        SELECT *
        FROM collection_requests
        WHERE user_id = ?
        ORDER BY date DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()


    connection.close()


    return render_template(
        "customer_dashboard.html",
        name=session.get("name"),
        location=session.get("location"),
        requests=requests_data
    )


# =========================================================
# REQUEST COLLECTION
# =========================================================

@app.route(
    "/request_collection",
    methods=["GET", "POST"]
)
def request_collection():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "user":

        return redirect("/login")


    # GET

    if request.method == "GET":

        return render_template(
            "request_collection.html",
            location=session.get("location")
        )


    # FORM DATA

    waste_type = request.form.get(
        "waste_type",
        ""
    ).strip()

    quantity = request.form.get(
        "quantity",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()


    # VALIDATION

    if (
        not waste_type
        or not quantity
        or not location
    ):

        return render_template(
            "request_collection.html",
            error="Please fill all required fields.",
            location=location
        )


    try:

        quantity = float(
            quantity
        )

    except ValueError:

        return render_template(
            "request_collection.html",
            error="Quantity must be a number.",
            location=location
        )


    if quantity <= 0:

        return render_template(
            "request_collection.html",
            error="Quantity must be greater than zero.",
            location=location
        )


    # COLLECTION DATE

    collection_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    connection = get_db_connection()


    try:

        connection.execute(
            """
            INSERT INTO collection_requests
            (
                user_id,
                waste_type,
                weight,
                quantity,
                location,
                description,
                collection_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                waste_type,
                quantity,
                quantity,
                location,
                description,
                collection_date,
                "Pending"
            )
        )


        connection.commit()

        connection.close()


    except Exception as e:

        connection.close()

        return render_template(
            "request_collection.html",
            error="Could not submit request: " + str(e),
            location=location
        )


    return render_template(
        "collection_submission.html",
        waste_type=waste_type,
        quantity=quantity,
        location=location,
        collection_date=collection_date
    )


# =========================================================
# CUSTOMER COLLECTION TRACKING
# =========================================================

@app.route(
    "/tracking"
)
def tracking():

    if "user_id" not in session:

        return redirect("/login")


    # CUSTOMER

    if session.get("role") == "user":

        connection = get_db_connection()


        collections = connection.execute(
            """
            SELECT *
            FROM collection_requests
            WHERE user_id = ?
            ORDER BY date DESC
            """,
            (
                session["user_id"],
            )
        ).fetchall()


        connection.close()


        return render_template(
            "tracking.html",
            collections=collections,
            user_view=True
        )


    # COLLECTOR

    if session.get("role") == "collector":

        return redirect(
            "/dashboard"
        )


    # RECYCLER

    return redirect(
        "/recycler"
    )


# =========================================================
# COLLECTOR DASHBOARD
# =========================================================

@app.route(
    "/dashboard"
)
def dashboard():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "collector":

        return redirect("/login")


    connection = get_db_connection()


    # COLLECTOR WASTE

    waste = connection.execute(
        """
        SELECT *
        FROM waste
        WHERE collector_id = ?
        ORDER BY date DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()


    # CUSTOMER REQUESTS

    collection_requests = connection.execute(
        """
        SELECT
            collection_requests.*,
            users.name AS user_name,
            users.mobile AS user_mobile
        FROM collection_requests
        JOIN users
        ON collection_requests.user_id = users.id
        ORDER BY collection_requests.date DESC
        """
    ).fetchall()


    connection.close()


    return render_template(
        "dashboard.html",
        name=session.get("name"),
        waste=waste,
        collection_requests=collection_requests
    )


# =========================================================
# ACCEPT COLLECTION REQUEST
# =========================================================

@app.route(
    "/accept_request/<int:request_id>",
    methods=["POST"]
)
def accept_request(request_id):

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "collector":

        return redirect("/login")


    connection = get_db_connection()


    collection_request = connection.execute(
        """
        SELECT *
        FROM collection_requests
        WHERE id = ?
        """,
        (
            request_id,
        )
    ).fetchone()


    if collection_request is None:

        connection.close()

        return redirect("/dashboard")


    if collection_request["status"] == "Pending":

        connection.execute(
            """
            UPDATE collection_requests
            SET status = ?
            WHERE id = ?
            """,
            (
                "Accepted",
                request_id
            )
        )

        connection.commit()


    connection.close()


    return redirect(
        "/dashboard"
    )


# =========================================================
# ADD WASTE
# =========================================================

@app.route(
    "/add_waste",
    methods=["GET", "POST"]
)
def add_waste():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "collector":

        return redirect("/login")


    if request.method == "POST":

        material = request.form.get(
            "material",
            ""
        ).strip()

        weight = request.form.get(
            "weight",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()


        if (
            not material
            or not weight
            or not location
        ):

            return render_template(
                "add_waste.html",
                error="Please fill all fields."
            )


        try:

            weight = float(
                weight
            )

        except ValueError:

            return render_template(
                "add_waste.html",
                error="Weight must be a number."
            )


        if weight <= 0:

            return render_template(
                "add_waste.html",
                error="Weight must be greater than zero."
            )


        connection = get_db_connection()


        connection.execute(
            """
            INSERT INTO waste
            (
                collector_id,
                material,
                weight,
                location,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                material,
                weight,
                location,
                "Collected"
            )
        )


        connection.commit()

        connection.close()


        return render_template(
            "add_waste.html",
            success="Waste added successfully!"
        )


    return render_template(
        "add_waste.html"
    )


# =========================================================
# AI WASTE IDENTIFICATION
# =========================================================

@app.route(
    "/identify",
    methods=["GET", "POST"]
)
def identify():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "collector":

        return redirect("/login")


    if request.method == "GET":

        return render_template(
            "identify.html"
        )


    image = request.files.get(
        "image"
    )


    if not image or image.filename == "":

        return render_template(
            "identify.html",
            error="Please select an image."
        )


    if model is None:

        return render_template(
            "identify.html",
            error="AI model could not be loaded. Make sure yolov8n.pt is inside the project folder."
        )


    filename = secure_filename(
        image.filename
    )


    if not filename:

        return render_template(
            "identify.html",
            error="Invalid image filename."
        )


    image_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    try:

        image.save(
            image_path
        )

    except Exception as e:

        return render_template(
            "identify.html",
            error="Could not save image: " + str(e)
        )


    try:

        results = model(
            image_path
        )


        detected_items = []


        for result in results:

            boxes = result.boxes


            if boxes is None:

                continue


            for box in boxes:

                class_id = int(
                    box.cls[0]
                )


                confidence = float(
                    box.conf[0]
                )


                class_name = model.names[
                    class_id
                ]


                detected_items.append(
                    {
                        "name": class_name,
                        "confidence": round(
                            confidence * 100,
                            2
                        )
                    }
                )


        if detected_items:

            return render_template(
                "identify.html",
                image_file=filename,
                detected_items=detected_items,
                message="Waste/object identified successfully!"
            )


        return render_template(
            "identify.html",
            image_file=filename,
            error="No object detected in the image."
        )


    except Exception as e:

        return render_template(
            "identify.html",
            error="AI identification failed: " + str(e)
        )


# =========================================================
# UPLOADED IMAGE
# =========================================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# =========================================================
# FAIR PRICE DETECTION
# =========================================================

@app.route(
    "/fair_price",
    methods=["GET", "POST"]
)
def fair_price():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "user":

        return redirect("/login")


    price = None

    rate = None

    quantity = None

    waste_type = None


    if request.method == "POST":

        waste_type = request.form.get(
            "waste_type",
            ""
        ).strip()


        quantity_text = request.form.get(
            "quantity",
            ""
        ).strip()


        if (
            not waste_type
            or not quantity_text
        ):

            return render_template(
                "fair_price.html",
                rates=FAIR_PRICE_RATES,
                error="Please select waste type and enter quantity."
            )


        try:

            quantity = float(
                quantity_text
            )

        except ValueError:

            return render_template(
                "fair_price.html",
                rates=FAIR_PRICE_RATES,
                error="Quantity must be a number."
            )


        if quantity <= 0:

            return render_template(
                "fair_price.html",
                rates=FAIR_PRICE_RATES,
                error="Quantity must be greater than zero."
            )


        rate = FAIR_PRICE_RATES.get(
            waste_type
        )


        if rate is None:

            return render_template(
                "fair_price.html",
                rates=FAIR_PRICE_RATES,
                error="Invalid waste type."
            )


        price = quantity * rate


    return render_template(
        "fair_price.html",
        rates=FAIR_PRICE_RATES,
        price=price,
        rate=rate,
        quantity=quantity,
        waste_type=waste_type
    )


# =========================================================
# VOICE ASSISTANT
# =========================================================

@app.route(
    "/voice_assistant"
)
def voice_assistant():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "user":

        return redirect("/login")


    return render_template(
        "voice_assistant.html"
    )


# =========================================================
# RECYCLER DASHBOARD
# =========================================================

@app.route(
    "/recycler"
)
def recycler():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "recycler":

        return redirect("/login")


    connection = get_db_connection()


    # Get all collected waste

    waste = connection.execute(
        """
        SELECT *
        FROM waste
        ORDER BY date DESC
        """
    ).fetchall()


    connection.close()


    return render_template(
        "recycler.html",
        waste=waste,
        collections=waste,
        name=session.get("name")
    )


# =========================================================
# UPDATE RECYCLING STATUS
# =========================================================

@app.route(
    "/update_recycling_status/<int:waste_id>",
    methods=["POST"]
)
def update_recycling_status(waste_id):

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "recycler":

        return redirect("/login")


    status = request.form.get(
        "status",
        ""
    ).strip()


    allowed_status = [

        "Collected",

        "Processing",

        "Recycled"

    ]


    if status not in allowed_status:

        return redirect(
            "/recycler"
        )


    connection = get_db_connection()


    try:

        connection.execute(
            """
            UPDATE waste
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                waste_id
            )
        )


        connection.commit()


    except Exception as e:

        print(
            "Status update error:",
            e
        )


    finally:

        connection.close()


    return redirect(
        "/recycler"
    )


# =========================================================
# COLLECTOR GPS - SHARE LOCATION PAGE
# =========================================================

@app.route(
    "/share_location"
)
def share_location():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "collector":

        return redirect("/login")


    return render_template(
        "share_location.html"
    )


# =========================================================
# COLLECTOR GPS - UPDATE LOCATION
# =========================================================

@app.route(
    "/update_location",
    methods=["POST"]
)
def update_location():

    if "user_id" not in session:

        return jsonify(
            {
                "success": False,
                "message": "Please login."
            }
        ), 401


    if session.get("role") != "collector":

        return jsonify(
            {
                "success": False,
                "message": "Only collectors can share location."
            }
        ), 403


    data = request.get_json()


    if not data:

        return jsonify(
            {
                "success": False,
                "message": "Location data missing."
            }
        ), 400


    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )


    if (
        latitude is None
        or longitude is None
    ):

        return jsonify(
            {
                "success": False,
                "message": "Location data missing."
            }
        ), 400


    connection = get_db_connection()


    try:

        # Remove previous location of this collector
        # so the database keeps only the latest position.

        connection.execute(
            """
            DELETE FROM collector_locations
            WHERE collector_id = ?
            """,
            (
                session["user_id"],
            )
        )


        connection.execute(
            """
            INSERT INTO collector_locations
            (
                collector_id,
                latitude,
                longitude
            )
            VALUES (?, ?, ?)
            """,
            (
                session["user_id"],
                float(latitude),
                float(longitude)
            )
        )


        connection.commit()


        connection.close()


        return jsonify(
            {
                "success": True,
                "message": "Location updated."
            }
        )


    except Exception as e:

        connection.close()


        return jsonify(
            {
                "success": False,
                "message": str(e)
            }
        ), 500


# =========================================================
# CUSTOMER - TRACK COLLECTOR PAGE
# =========================================================

@app.route(
    "/track_collector"
)
def track_collector():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "user":

        return redirect("/login")


    return render_template(
        "track_collector.html"
    )


# =========================================================
# CUSTOMER - GET COLLECTOR LOCATION
# =========================================================

@app.route(
    "/get_collector_location"
)
def get_collector_location():

    if "user_id" not in session:

        return jsonify(
            {
                "success": False,
                "message": "Please login."
            }
        ), 401


    if session.get("role") != "user":

        return jsonify(
            {
                "success": False,
                "message": "Only customers can view collector location."
            }
        ), 403


    connection = get_db_connection()


    try:

        location = connection.execute(
            """
            SELECT
                collector_locations.latitude,
                collector_locations.longitude,
                collector_locations.updated_at,
                users.name AS collector_name
            FROM collector_locations
            JOIN users
            ON collector_locations.collector_id = users.id
            WHERE users.role = 'collector'
            ORDER BY collector_locations.updated_at DESC
            LIMIT 1
            """
        ).fetchone()


        connection.close()


        if location:

            return jsonify(
                {
                    "success": True,

                    "latitude":
                        location["latitude"],

                    "longitude":
                        location["longitude"],

                    "updated_at":
                        location["updated_at"],

                    "collector_name":
                        location["collector_name"]
                }
            )


        return jsonify(
            {
                "success": False,
                "message":
                    "Collector has not shared a location yet."
            }
        )


    except Exception as e:

        connection.close()


        return jsonify(
            {
                "success": False,
                "message": str(e)
            }
        ), 500


# =========================================================
# RECYCLER LOGOUT / HOME REDIRECT
# =========================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        "/"
    )


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
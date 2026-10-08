from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import (
    create_tables,
    insert_user,
    get_user_by_email,
    get_workers,
    get_courses
)


# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(
    __name__,
    static_folder="styles",
    static_url_path="/static"
)

app.secret_key = "school-management-secret-key"


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ==========================================================
# REGISTER
# ==========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Data comes from registration.html
        name = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        if not name:

            return render_template(
                "registration.html",
                error="Please enter your name.",
                username_value=name,
                email_value=email
            )

        if not email:

            return render_template(
                "registration.html",
                error="Please enter your email.",
                username_value=name,
                email_value=email
            )

        if "@" not in email:

            return render_template(
                "registration.html",
                error="Please enter a valid email.",
                username_value=name,
                email_value=email
            )

        if len(password) < 8:

            return render_template(
                "registration.html",
                error="Password must contain at least 8 characters.",
                username_value=name,
                email_value=email
            )

        if password != confirm_password:

            return render_template(
                "registration.html",
                error="Passwords do not match.",
                username_value=name,
                email_value=email
            )

        # ----------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------

        hashed_password = generate_password_hash(password)

        # ----------------------------------------------
        # SEND DATA TO DATABASE.PY
        # ----------------------------------------------

        success, message = insert_user(
            name=name,
            email=email,
            password=hashed_password,
            role="student"
        )

        if not success:

            return render_template(
                "registration.html",
                error=message,
                username_value=name,
                email_value=email
            )

        # ----------------------------------------------
        # SUCCESS
        # ----------------------------------------------

        return redirect(
            url_for("login")
        )

    return render_template(
        "registration.html",
        username_value="",
        email_value=""
    )


# ==========================================================
# LOGIN
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = get_user_by_email(email)

        if user is None:

            return render_template(
                "login.html",
                error="Incorrect email or password.",
                email_value=email
            )

        if not check_password_hash(
            user["password"],
            password
        ):

            return render_template(
                "login.html",
                error="Incorrect email or password.",
                email_value=email
            )

        # ----------------------------------------------
        # LOGIN SUCCESSFUL
        # ----------------------------------------------

        session.clear()

        session["user_id"] = user["id"]
        session["username"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html",
        email_value=""
    )


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    # Get data from database.py
    workers = get_workers()
    courses = get_courses()

    # ----------------------------------------------
    # WORKER STATISTICS
    # ----------------------------------------------

    active_workers = sum(
        worker["status"] == "active"
        for worker in workers
    )

    inactive_workers = (
        len(workers) - active_workers
    )

    # ----------------------------------------------
    # DEPARTMENTS
    # ----------------------------------------------

    department_counts = {}

    for worker in workers:

        department = (
            worker["department"]
            or "Unassigned"
        )

        department_counts[department] = (
            department_counts.get(
                department,
                0
            ) + 1
        )

    departments = []

    for name, count in department_counts.items():

        percentage = 0

        if workers:

            percentage = round(
                count / len(workers) * 100
            )

        departments.append({
            "name": name,
            "count": count,
            "percentage": percentage
        })

    # ----------------------------------------------
    # SEND DATA TO DASHBOARD
    # ----------------------------------------------

    return render_template(
        "index.html",

        current_user={
            "name": session["username"],
            "email": session["email"],
            "role": session["role"]
        },

        workers=workers,
        courses=courses,
        departments=departments,

        total_workers=len(workers),
        total_courses=len(courses),

        active_workers=active_workers,
        inactive_workers=inactive_workers
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    create_tables()

    app.run(debug=True) 
    
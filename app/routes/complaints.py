from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import query

bp = Blueprint("complaints", __name__, url_prefix="/complaints")


# -----------------------------
#       LIST COMPLAINTS
# -----------------------------
@bp.route("/")
@login_required
def list_complaints():
    if current_user.is_admin:
        return redirect(url_for("admin.admin_complaints"))
    else:
        return redirect(url_for("user.user_dashboard"))


# -----------------------------
#      FILE NEW COMPLAINT
# -----------------------------
@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_complaint():
    if current_user.is_admin:
        return "Only users can file a complaint!"
    
    departments = query("SELECT department_id, department_name FROM departments", fetchall=True)

    if request.method == "POST" and not current_user.is_admin:

        title = request.form["title"]
        department_id = request.form["department_id"]
        description = request.form["description"]

        query(
            """
            INSERT INTO complaints (user_id, department_id, title, description)
            VALUES (%s, %s, %s, %s)
            """,
            (current_user.id, department_id, title, description),
            commit=True
        )

        flash("Complaint filed successfully!", "success")
        return redirect(url_for("user.user_dashboard"))

    return render_template("new_complaint.html", departments=departments)

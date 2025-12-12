from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.utils.email import send_notification
from app.db import query
import os

bp = Blueprint("complaints", __name__, url_prefix="/complaints")


# -------------------------------------------------
#                LIST COMPLAINTS
# -------------------------------------------------
@bp.route("/")
@login_required
def list_complaints():
    if current_user.is_admin:
        return redirect(url_for("admin.admin_complaints"))
    elif current_user.is_staff:
        return redirect(url_for("staff.staff_dashboard"))
    return redirect(url_for("user.user_dashboard"))


# -------------------------------------------------
#               FILE NEW COMPLAINT
# -------------------------------------------------
@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_complaint():
    if current_user.is_admin:
        return "Only users can file a complaint!"

    departments = query(
        "SELECT department_id, department_name FROM departments", fetchall=True
    )

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        department_id = request.form.get("department_id")
        description = request.form.get("description", "").strip()

        file = request.files.get("attachment")
        attachment_name = None

        if file and file.filename:
            safe_name = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
            file.save(upload_path)
            attachment_name = safe_name

        # Insert complaint
        latest_complaint = query(
            """
            INSERT INTO complaints (user_id, department_id, title, description, attachment, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING complaint_id, status, title
            """,
            (current_user.id, department_id, title, description, attachment_name),
            fetchone=True,
            commit=True,
        )

        # Fetch user + complaint info
        user_data = query(
            """
            SELECT u.username, u.email, c.complaint_id, c.title, c.status
            FROM users u
            JOIN complaints c ON u.user_id = c.user_id
            WHERE c.complaint_id = %s
            """,
            (latest_complaint["complaint_id"],),
            fetchone=True,
        )

        # Email notification
        send_notification(
            to=user_data["email"],
            subject="Complaint Filed Successfully",
            body=(
                f"Hello {user_data['username']},\n\n"
                f"Your complaint titled '{user_data['title']}' has been filed.\n"
                f"Current Status: {user_data['status']}.\n"
                f"We will keep you updated on any changes.\n\n"
                f"Regards,\nAdmin Team"
            ),
        )

        flash("Complaint filed successfully!", "success")
        return redirect(url_for("user.user_dashboard"))

    return render_template("new_complaint.html", departments=departments)

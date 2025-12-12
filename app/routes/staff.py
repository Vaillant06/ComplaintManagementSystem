from flask import Blueprint, flash, redirect, url_for, render_template, abort, request
from flask_login import login_required, current_user
from app.extensions import bcrypt
from datetime import timedelta
from app.utils.email import send_notification
from app.db import query

bp = Blueprint("staff", __name__, url_prefix="/staff")

IST = timedelta(hours=5, minutes=30)


def to_ist(dt):
    return (dt + IST).strftime("%H:%M | %d - %B - %Y") if dt else None


@bp.route("/")
@login_required
def staff_dashboard():
    if not current_user.is_staff:
        abort(403)

    ITEMS_PER_PAGE = 10
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * ITEMS_PER_PAGE

    staff = query(
        "SELECT * FROM staff WHERE staff_id=%s", (current_user.id,), fetchone=True
    )

    complaints = query(
        """
        SELECT c.*, u.username, d.department_name
        FROM complaints c
        JOIN users u ON u.user_id = c.user_id
        JOIN departments d ON c.department_id = d.department_id
        WHERE c.department_id = (
            SELECT department_id FROM staff WHERE staff_id=%s
        )
        AND c.status IN ('In Progress', 'Resolved')
        ORDER BY c.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (current_user.id, ITEMS_PER_PAGE, offset),
        fetchall=True,
    )

    total_complaints = query(
        """
        SELECT COUNT(*)
        FROM complaints c
        JOIN users u ON u.user_id = c.user_id
        WHERE c.department_id = (
            SELECT department_id FROM staff WHERE staff_id=%s
        )
        AND c.status IN ('In Progress', 'Resolved')
        """,
        (current_user.id,),
        fetchone=True,
    )[0]

    total_pages = (total_complaints + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    new_complaints_count = query(
        """
        SELECT COUNT(*)
        FROM complaints c
        JOIN users u ON u.user_id = c.user_id
        WHERE c.department_id = (
            SELECT department_id FROM staff WHERE staff_id=%s
        )
        AND c.status IN ('In Progress', 'Resolved')
        AND c.assigned_at >= CURRENT_DATE
        """,
        (staff["staff_id"],),
        fetchone=True,
    )[0]

    # Format timestamps
    for c in complaints:
        c["created_at"] = to_ist(c["created_at"])
        if c.get("assigned_at"):
            c["assigned_at"] = to_ist(c["assigned_at"])
        if c.get("resolved_at"):
            c["resolved_at"] = to_ist(c["resolved_at"])

    if staff.get("last_login"):
        staff["last_login"] = (staff["last_login"] + IST).strftime("%H:%M | %d-%B-%Y")

    return render_template(
        "staff_dashboard.html",
        complaints=complaints,
        total_count=total_complaints,
        new_complaints_count=new_complaints_count,
        staff=staff,
        total_pages=total_pages,
        page=page,
    )


@bp.route("/update_status/<int:complaint_id>", methods=["GET", "POST"])
@login_required
def update_status(complaint_id):
    if not current_user.is_staff:
        abort(403)

    staff = query(
        "SELECT * FROM staff WHERE staff_id=%s", (current_user.id,), fetchone=True
    )

    department = query(
        "SELECT * FROM departments WHERE department_id=%s",
        (staff["department_id"],),
        fetchone=True,
    )

    complaint = query(
        "SELECT * FROM complaints WHERE complaint_id=%s", (complaint_id,), fetchone=True
    )

    if request.method == "POST":
        new_status = request.form["status"]
        staff_comment = request.form["staff_comment"]
        password = request.form["password"]

        old_status = query(
            "SELECT status FROM complaints WHERE complaint_id=%s",
            (complaint_id,),
            fetchone=True,
        )[0]

        # Password verification
        if not bcrypt.check_password_hash(staff["password"], password):
            flash("Password mismatch!", "alert")
            return redirect(url_for("staff.update_status", complaint_id=complaint_id))

        # No status change
        if old_status == new_status:
            flash("Status unchanged!", "info")
            return redirect(url_for("staff.update_status", complaint_id=complaint_id))

        # Update complaint
        query(
            """
            UPDATE complaints
            SET status=%s,
                staff_comment=%s,
                assigned_to=NULL,
                resolved_at = CASE WHEN %s = 'Resolved' THEN NOW() ELSE NULL END
            WHERE complaint_id=%s
            """,
            (new_status, staff_comment, new_status, complaint_id),
            commit=True,
        )

        user_data = query(
            """
            SELECT u.email, u.username, c.title
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.complaint_id=%s
            """,
            (complaint_id,),
            fetchone=True,
        )

        # Send user email
        if user_data:
            send_notification(
                to=user_data["email"],
                subject="Complaint Status Updated",
                body=(
                    f"Hello {user_data['username']},\n\n"
                    f"Your complaint titled '{user_data['title']}' has been updated.\n"
                    f"Old Status: {old_status}\n"
                    f"New Status: {new_status}\n"
                    f"View your complaint for more details.\n\n"
                    f"Regards,\nAdmin Team"
                ),
            )

        flash("Status updated!", "success")
        return redirect(url_for("staff.staff_dashboard"))

    return render_template(
        "staff_update_status.html",
        staff=staff,
        department=department,
        complaint=complaint,
    )

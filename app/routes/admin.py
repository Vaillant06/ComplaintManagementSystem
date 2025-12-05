from flask import Blueprint, flash, redirect, url_for, render_template, abort, request
from flask_login import login_required , current_user
from datetime import timedelta
from app.db import query

bp = Blueprint("admin", __name__, url_prefix="/admin")


# -----------------------------
#       ADMIN DASHBOARD
# -----------------------------
@bp.route("/")
@login_required
def admin_home():
    if not current_user.is_admin:
        abort(403)
    
    admin = query(
        "SELECT last_login FROM admins WHERE admin_id=%s",
        (current_user.id,),
        fetchone=True
    )

    last_login = admin["last_login"]

    if last_login:
        last_login = (last_login + timedelta(hours=5, minutes=30))\
                        .strftime("%H:%M | %d-%m-%Y")

    return render_template("admin_dashboard.html", last_login=last_login)


# -----------------------------
#     ADMIN VIEW COMPLAINTS
# -----------------------------
@bp.route("/complaints", methods=["GET"])
@login_required
def admin_complaints():
    if not current_user.is_admin:      
        abort(403)

    ITEMS_PER_PAGE = 10
    status = request.args.get("status")

    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * ITEMS_PER_PAGE

    total = query("SELECT COUNT(*) FROM complaints", fetchone=True)[0]
    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    if status:
        rows = query(
            """
            SELECT c.*, u.username, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE c.status = %s
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (status, ITEMS_PER_PAGE, offset),
            fetchall=True,
        )

    else:
        rows = query(
            """
            SELECT c.*, u.username, d.department_id, d.department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            JOIN departments d ON d.department_id = c.department_id
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (ITEMS_PER_PAGE, offset),
            fetchall=True,
        )

    total = query(
        "SELECT count(*) FROM complaints",
        fetchone=True
    )[0]

    for c in rows:
        c["created_at"] = (c["created_at"] + timedelta(hours=5, minutes=30))\
                            .strftime("%H:%M | %d-%B-%Y")

    return render_template("admin_complaints.html", complaints=rows, status=status, total=total, total_pages=total_pages, page=page)


# -----------------------------
#      COMPLAINTS SUMMARY
# -----------------------------
@bp.route("complaints_summary", methods=["GET", "POST"])
@login_required
def complaints_summary():
    if not current_user.is_admin:
        abort(403)

    pending = query(
        "SELECT count(*) FROM complaints WHERE status='Pending'",
        fetchone=True
    )[0]

    progress = query(
        "SELECT count(*) FROM complaints WHERE status='In Progress'",
        fetchone=True
    )[0]

    resolved = query(
        "SELECT count(*) FROM complaints WHERE status='Resolved'",
        fetchone=True
    )[0]

    rejected = query(
        "SELECT count(*) FROM complaints WHERE status='Rejected'",
        fetchone=True
    )[0]

    total = query(
        "SELECT count(*) FROM complaints",
        fetchone=True
    )[0]

    return render_template("complaints_summary.html", pending=pending, progress=progress, resolved=resolved, rejected=rejected, total=total)


# -----------------------------
#    EDIT COMPLAINT STATUS
# -----------------------------
@bp.route("/complaints/<int:complaint_id>/status", methods=["GET", "POST"])
@login_required
def edit_status(complaint_id):
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        new_status = request.form["status"]
        query(
            "UPDATE complaints SET status=%s WHERE complaint_id=%s",
            (new_status, complaint_id),
            commit=True
        )

        if new_status == "Resolved":
            query(
                "UPDATE complaints SET admin_comment = %s WHERE complaint_id = %s",
                ("Resolved the Issue", complaint_id),
                commit=True
            )
        elif new_status == "Rejected":
            query(
                "UPDATE complaints SET admin_comment = %s WHERE complaint_id = %s",
                ("Rejected due to duplicate complaint", complaint_id),
                commit=True
            )

        flash("Status updated successfully!", "success")
        return redirect(url_for("admin.admin_complaints"))

    comp = query(
        "SELECT * FROM complaints WHERE complaint_id=%s", (complaint_id,), fetchone=True
    )

    return render_template("edit_status.html", complaint=comp)


# ------------------------------
#       ADMIN ADD COMMENT
# ------------------------------
@bp.route("/complaints/<int:complaint_id>/add_comment", methods=["POST"])
@login_required
def add_comment(complaint_id):
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        admin_comment = request.form["admin_comment"].strip()

        query(
            "UPDATE complaints SET admin_comment=%s WHERE complaint_id=%s",
            (admin_comment, complaint_id,),
            commit=True
        )

    flash("Comment updated successfully", "success")
    return redirect(url_for("admin.admin_complaints"))


# -----------------------------
#    ADMIN ASSIGN COMPLAINT
# -----------------------------
@bp.route(
    "/complaints/<int:complaint_id>/<int:department_id>/assign", methods=["GET", "POST"]
)
@login_required
def assign_complaint(complaint_id, department_id):
    if not current_user.is_admin:
        abort(403)

    staff = query(
        "SELECT staff_id FROM staff WHERE department_id=%s LIMIT 1",
        (department_id,),
        fetchone=True,
    )

    if not staff:
        flash("No staff found in this department!", "danger")
        return redirect(url_for("admin.admin_complaints"))

    staff_id = staff["staff_id"]

    query(
        "UPDATE complaints SET status='In Progress', assigned_to=%s, assigned_at=NOW() WHERE complaint_id=%s",
        (staff_id, complaint_id),
        commit=True,
    )

    flash("Complaint assigned successfully!", "success")
    return redirect(url_for("admin.admin_complaints"))

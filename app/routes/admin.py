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
    if current_user.role != "admin":
        abort(403)
        
    flash("Admin login successful", "success")
    return render_template("admin_dashboard.html")


# -----------------------------
#     ADMIN VIEW COMPLAINTS
# -----------------------------
@bp.route("/complaints", methods=["GET"])
@login_required
def admin_complaints():
    if current_user.role != "admin":      
        abort(403)
    
    status = request.args.get("status")

    if status:
        rows = query(
            """
            SELECT c.*, u.name AS user_name, d.name AS department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN departments d ON d.id = c.department_id
            WHERE c.status = %s
            ORDER BY c.created_at DESC
            """,
            (status,),
            fetchall=True
        )
    else:
        rows = query(
            """
            SELECT c.*, u.name AS user_name, d.name AS department_name
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            JOIN departments d ON d.id = c.department_id
            ORDER BY c.created_at DESC
            """,
            fetchall=True
        )


    for c in rows:
        c["created_at"] = (c["created_at"] + timedelta(hours=5, minutes=30))\
                            .strftime("%H:%M | %d-%m-%Y")

     
    return render_template("admin_complaints.html", complaints=rows, status=status)


# -----------------------------
#      COMPLAINTS SUMMARY
# -----------------------------
@bp.route("complaints_summary", methods=["GET", "POST"])
@login_required
def complaints_summary():
    if current_user.role != "admin":
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
    if current_user.role != "admin":
        abort(403)

    if request.method == "POST":
        new_status = request.form["status"]
        query(
            "UPDATE complaints SET status=%s WHERE id=%s",
            (new_status, complaint_id),
            commit=True
        )
        flash("Status updated successfully!", "success")
        return redirect(url_for("admin.admin_complaints"))

    comp = query("SELECT * FROM complaints WHERE id=%s", (complaint_id,), fetchone=True)
    return render_template("edit_status.html", complaint=comp)


#------------------------------
#       ADMIN ADD COMMENT
#------------------------------
@bp.route("/complaints/<int:complaint_id>/add_comment", methods=["POST"])
@login_required
def add_comment(complaint_id):
    if current_user.role != "admin":
        abort(403)
    
    if request.method == "POST":
        admin_comment = request.form["admin_comment"].strip()

        query(
            "UPDATE complaints SET admin_comment=%s WHERE id=%s",
            (admin_comment, complaint_id,),
            commit=True
        )

    flash("Comment added successfully", "success")
    return redirect(url_for("admin.admin_complaints"))


# -----------------------------
#    ADMIN ASSIGN COMPLAINT
# -----------------------------
@bp.route("/complaints/<int:complaint_id>/assign", methods=["GET", "POST"])
@login_required
def assign_complaint(complaint_id, admin_comment):
    if current_user.role != "admin":
        abort(403)

    query(
        "UPDATE complaints SET status='In Progress' WHERE id=%s",
        (complaint_id,),
        commit=True
    )

    query(
        "UPDATE complaints SET assigned_to='staff' WHERE id=%s",
        (complaint_id,),
        commit=True 
    )

    flash("Assigned task successfully!", "success")

    return redirect(url_for("admin.admin_complaints"))

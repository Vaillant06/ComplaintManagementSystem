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
@bp.route("/complaints")
@login_required
def admin_complaints():
    if current_user.role != "admin":      
        abort(403)
    
    rows = query(
        "SELECT c.*, u.name as user_name FROM complaints c JOIN users u ON c.user_id = u.id ORDER BY c.created_at DESC",
        fetchall=True
    )

    for c in rows:
        c["created_at"] = (c["created_at"] + timedelta(hours=5, minutes=30))\
                            .strftime("%H:%M | %d-%m-%Y")

     
    return render_template("admin_complaints.html", complaints=rows)


# -----------------------------
#      COMPLAINTS SUMMARY
# -----------------------------
@bp.route("complaints_summary", methods=["GET", "POST"])
@login_required
def complaints_summary():
    return "Complaints summary here"


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


# -----------------------------
#    ADMIN ASSIGN COMPLAINT
# -----------------------------
@bp.route("/complaints/<int:complaint_id>/assign", methods=["GET", "POST"])
@login_required
def assign_complaint(complaint_id):
    if current_user.role != "admin":
        abort(403)

    query(
        "UPDATE complaints SET status='In Progress' WHERE id=%s",
        (complaint_id,),
        commit=True
    )

    flash("Assigned task successfully!", "success")

    return redirect(url_for("admin.admin_complaints"))

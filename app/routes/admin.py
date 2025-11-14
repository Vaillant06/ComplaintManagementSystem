from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import login_required , current_user
from app.db import query

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/")
@login_required
def admin_home():
    if current_user.role != "admin":
        abort(403)
        
    flash("Admin login successful", "success")
    return render_template("admin_dashboard.html")

@bp.route("/complaints")
@login_required
def admin_complaints():
    if current_user.role != "admin":      
        abort(403)
    
    rows = query(
        "SELECT c.*, u.name as user_name FROM complaints c JOIN users u ON c.user_id = u.id ORDER BY c.created_at DESC",
        fetchall=True
    )
     
    return render_template("admin_complaints.html", complaints=rows)
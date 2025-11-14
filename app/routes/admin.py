from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required 

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/")
@login_required
def admin_home():
    flash("Admin login successful", "success")
    return render_template('admin_dashboard.html')

@login_required
def view_complaints():
     return redirect(url_for("complaints.list_complaints"))
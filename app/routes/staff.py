from flask import Blueprint, flash, redirect, url_for, render_template, abort, request
from flask_login import login_required, current_user
from datetime import timedelta
from app.utils.email import send_notification
from app.db import query


bp = Blueprint("staff", __name__, url_prefix="/staff")

@bp.route("/")
@login_required
def staff_dashboard():
    if not current_user.is_staff:
        abort(403)

    complaints = query(
        """
        SELECT c.*, u.username AS user_name 
        FROM complaints c
        JOIN users u ON u.user_id = c.user_id
        WHERE c.department_id = (
            SELECT department_id FROM staff WHERE staff_id=%s
        )
        ORDER BY c.created_at DESC
    """,
        (current_user.id,),
        fetchall=True,
    )

    return render_template("staff_dashboard.html", complaints=complaints)

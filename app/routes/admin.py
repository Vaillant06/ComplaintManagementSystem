from flask import Blueprint, flash, redirect, url_for, render_template, abort, request
from flask_login import login_required , current_user
from datetime import timedelta
from app.utils.email import send_notification
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

    if status:
        total_count = query(
            """
            SELECT COUNT(*)
            FROM complaints c
            JOIN departments d ON c.department_id = d.department_id
            JOIN users u ON c.user_id = u.user_id
            WHERE c.status = %s
            """,
            (status,),
            fetchone=True
        )[0]
    else:
        total_count = query(
            """
            SELECT COUNT(*)
            FROM complaints c
            JOIN departments d ON c.department_id = d.department_id
            JOIN users u ON c.user_id = u.user_id
            """,
            fetchone=True
        )[0]


    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

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

    electrical = query(
        "SELECT count(*) FROM complaints WHERE department_id=1",
        fetchone=True
    )[0]

    water =  query(
        "SELECT count(*) FROM complaints WHERE department_id=2",
        fetchone=True
    )[0]

    public_works = query(
        "SELECT count(*) FROM complaints WHERE department_id=3",
        fetchone=True
    )[0]

    health_care = query(
        "SELECT count(*) FROM complaints WHERE department_id=4",
        fetchone=True
    )[0]

    total = query(
        "SELECT count(*) FROM complaints",
        fetchone=True
    )[0]

    electrical_pending = query(
        "SELECT count(*) FROM complaints WHERE department_id=1 AND status='Pending'",
        fetchone=True
    )[0]

    electrical_progress = query(
        "SELECT count(*) FROM complaints WHERE department_id=1 AND status='In Progress'",
        fetchone=True
    )[0]

    electrical_resolved = query(            
        "SELECT count(*) FROM complaints WHERE department_id=1 AND status='Resolved'",
        fetchone=True
    )[0]    

    electrical_rejected = query(        
        "SELECT count(*) FROM complaints WHERE department_id=1 AND status='Rejected'",
        fetchone=True
    )[0]   

    water_pending = query(
        "SELECT count(*) FROM complaints WHERE department_id=2 AND status='Pending'",
        fetchone=True,
    )[0]

    water_progress = query(
        "SELECT count(*) FROM complaints WHERE department_id=2 AND status='In Progress'",
        fetchone=True,
    )[0]

    water_resolved = query(
        "SELECT count(*) FROM complaints WHERE department_id=2 AND status='Resolved'",
        fetchone=True,
    )[0]

    water_rejected = query(
        "SELECT count(*) FROM complaints WHERE department_id=2 AND status='Rejected'",
        fetchone=True,
    )[0]

    pw_pending = query(
        "SELECT count(*) FROM complaints WHERE department_id=3 AND status='Pending'",
        fetchone=True,
    )[0]

    pw_progress = query(
        "SELECT count(*) FROM complaints WHERE department_id=3 AND status='In Progress'",
        fetchone=True,
    )[0]

    pw_resolved = query(
        "SELECT count(*) FROM complaints WHERE department_id=3 AND status='Resolved'",
        fetchone=True,
    )[0]

    pw_rejected = query(
        "SELECT count(*) FROM complaints WHERE department_id=3 AND status='Rejected'",
        fetchone=True,
    )[0]

    hc_pending = query(
        "SELECT count(*) FROM complaints WHERE department_id=4 AND status='Pending'",
        fetchone=True,
    )[0]

    hc_progress = query(
        "SELECT count(*) FROM complaints WHERE department_id=4 AND status='In Progress'",
        fetchone=True,
    )[0]

    hc_resolved = query(
        "SELECT count(*) FROM complaints WHERE department_id=4 AND status='Resolved'",
        fetchone=True,
    )[0]

    hc_rejected = query(
        "SELECT count(*) FROM complaints WHERE department_id=4 AND status='Rejected'",
        fetchone=True,
    )[0]

    return render_template(
        "complaints_summary.html", 
        pending=pending, 
        progress=progress, 
        resolved=resolved, 
        rejected=rejected, 
        electrical=electrical, 
        water=water, 
        public_works=public_works,      
        health_care=health_care,
        electrical_pending=electrical_pending,
        electrical_progress=electrical_progress,
        electrical_resolved=electrical_resolved,    
        electrical_rejected=electrical_rejected,
        water_pending=water_pending,
        water_progress=water_progress,
        water_resolved=water_resolved,
        water_rejected=water_rejected,
        pw_pending=pw_pending,
        pw_progress=pw_progress,
        pw_resolved=pw_resolved,
        pw_rejected=pw_rejected,
        hc_pending=hc_pending,
        hc_progress=hc_progress,
        hc_resolved=hc_resolved,
        hc_rejected=hc_rejected,
        total=total
    )

# -----------------------------
#      COMPLAINT ANALYTICS
# -----------------------------
@bp.route("/complaints_analytics")
@login_required
def complaints_analytics():
    if not current_user.is_admin:
        abort(403)

    rows = query(
        """
        SELECT d.department_name, COUNT(*) AS total
        FROM complaints c
        JOIN departments d ON c.department_id = d.department_id
        GROUP BY d.department_name
        ORDER BY d.department_name
        """,
        fetchall=True,
    )

    labels = [row["department_name"] for row in rows]
    counts = [row["total"] for row in rows]

    daily_rows = query(
        """
    SELECT 
        TO_CHAR(created_at, 'DD Mon') AS day,
        DATE(created_at) AS day_order,
        COUNT(*) AS total
    FROM complaints
    GROUP BY day, day_order
    ORDER BY day_order;
    """,
        fetchall=True,
    )

    trend_labels = [row["day"] for row in daily_rows]
    trend_counts = [row["total"] for row in daily_rows]

    status_rows = query(
        """
    SELECT status, COUNT(*) AS total
    FROM complaints
    GROUP BY status
    ORDER BY status;
    """,
        fetchall=True,
    )

    status_labels = [row["status"] for row in status_rows]
    status_counts = [row["total"] for row in status_rows]

    return render_template(
        "complaints_analytics.html",
        labels=labels,
        counts=counts,
        trend_labels=trend_labels,
        trend_counts=trend_counts,
        status_labels=status_labels,
        status_counts=status_counts,
    )


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

        old_status = query(
            "SELECT status FROM complaints WHERE complaint_id=%s",
            (complaint_id,),
            fetchone=True,
        )["status"]

        if new_status == old_status:
            flash("Status is unchanged.", "info")
            return redirect(url_for("admin.admin_complaints"))

        else:
            complaint_data = query(
                """
                SELECT u.email, u.username, c.title, c.department_id
                FROM complaints c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.complaint_id = %s
                """,
                (complaint_id,),
                fetchone=True,
            )

            department_id = complaint_data["department_id"]

            staff_id = query(
                """
                SELECT staff_id
                FROM staff  
                WHERE department_id = %s
                """,
                (department_id,),
                fetchone=True,
            )[0]

            if complaint_data:
                send_notification(
                    to=complaint_data["email"],
                    subject="Complaint Status Updated",
                    body=f"Hello {complaint_data['username']},\n\n"
                    f"Your complaint titled '{complaint_data['title']}' has been updated.\n"
                    f"Old Status: {old_status}\n"
                    f"New Status: {new_status}.\n"
                    f"View your complaint for more details.\n"
                    f"Regards,\nAdmin Team",
                )

                query(
                    "UPDATE complaints SET status=%s, assigned_to=%s, assigned_at=NOW() WHERE complaint_id=%s",
                    (new_status, staff_id, complaint_id),
                    commit=True,
                )

            if new_status == "Rejected":
                query(
                    """
                    UPDATE complaints
                    SET assigned_to=NULL, assigned_at=NULL, admin_comment='Rejected due to duplicate complaint'
                    WHERE complaint_id=%s 
                    """,
                    (complaint_id,),
                    commit=True,
                )

            elif new_status == "Resolved":
                query(
                    """
                    UPDATE complaints
                    SET assigned_to=NULL, assigned_at=NULL, resolved_at=NOW(), admin_comment='Resolved the issue'
                    WHERE complaint_id=%s 
                    """,
                    (complaint_id,),
                    commit=True,
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

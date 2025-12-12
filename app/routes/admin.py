from flask import Blueprint, flash, redirect, url_for, render_template, abort, request
from flask_login import login_required, current_user
from datetime import timedelta
from app.utils.email import send_notification
from app.db import query


bp = Blueprint("admin", __name__, url_prefix="/admin")

IST_OFFSET = timedelta(hours=5, minutes=30)


def to_ist(dt):
    return (dt + IST_OFFSET).strftime("%H:%M | %d-%b-%Y") if dt else None


# ------------------------------------
#            ADMIN DASHBOARD
# ------------------------------------
@bp.route("/")
@login_required
def admin_home():
    if not current_user.is_admin:
        abort(403)

    admin = query(
        "SELECT last_login FROM admins WHERE admin_id=%s",
        (current_user.id,),
        fetchone=True,
    )

    last_login = to_ist(admin["last_login"]) if admin else None
    return render_template("admin_dashboard.html", last_login=last_login)


# ------------------------------------
#         VIEW COMPLAINTS
# ------------------------------------
@bp.route("/complaints")
@login_required
def admin_complaints():
    if not current_user.is_admin:
        abort(403)

    ITEMS_PER_PAGE = 10
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * ITEMS_PER_PAGE

    # Total count
    where_clause = "WHERE c.status = %s" if status else ""
    params = (status,) if status else ()

    total_count = query(
        f"""
        SELECT COUNT(*)
        FROM complaints c
        JOIN departments d ON c.department_id = d.department_id
        JOIN users u ON c.user_id = u.user_id
        {where_clause}
        """,
        params,
        fetchone=True,
    )[0]

    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # Query rows
    rows = query(
        f"""
        SELECT c.*, u.username, d.department_name
        FROM complaints c
        JOIN users u ON c.user_id = u.user_id
        JOIN departments d ON d.department_id = c.department_id
        {where_clause}
        ORDER BY c.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, ITEMS_PER_PAGE, offset),
        fetchall=True,
    )

    # Format timestamps
    for c in rows:
        c["created_at"] = to_ist(c["created_at"])
        if c.get("assigned_at"):
            c["assigned_at"] = to_ist(c["assigned_at"])
        if c.get("resolved_at"):
            c["resolved_at"] = to_ist(c["resolved_at"])

    total = query("SELECT COUNT(*) FROM complaints", fetchone=True)[0]

    return render_template(
        "admin_complaints.html",
        complaints=rows,
        status=status,
        total=total,
        total_pages=total_pages,
        page=page,
    )


# ------------------------------------
#        COMPLAINT SUMMARIES
# ------------------------------------
@bp.route("/complaints_summary")
@login_required
def complaints_summary():
    if not current_user.is_admin:
        abort(403)

    statuses = ["Pending", "In Progress", "Resolved", "Rejected"]
    departments = [1, 2, 3, 4]

    # Summary counts
    status_counts = {
        s: query(
            "SELECT COUNT(*) FROM complaints WHERE status=%s", (s,), fetchone=True
        )[0]
        for s in statuses
    }

    dept_counts = {
        d: query(
            "SELECT COUNT(*) FROM complaints WHERE department_id=%s",
            (d,),
            fetchone=True,
        )[0]
        for d in departments
    }

    # Status per department
    dept_status_counts = {
        d: {
            s: query(
                "SELECT COUNT(*) FROM complaints WHERE department_id=%s AND status=%s",
                (d, s),
                fetchone=True,
            )[0]
            for s in statuses
        }
        for d in departments
    }

    total = query("SELECT COUNT(*) FROM complaints", fetchone=True)[0]

    return render_template(
        "complaints_summary.html",
        pending=status_counts["Pending"],
        progress=status_counts["In Progress"],
        resolved=status_counts["Resolved"],
        rejected=status_counts["Rejected"],
        electrical=dept_counts[1],
        water=dept_counts[2],
        public_works=dept_counts[3],
        health_care=dept_counts[4],
        electrical_pending=dept_status_counts[1]["Pending"],
        electrical_progress=dept_status_counts[1]["In Progress"],
        electrical_resolved=dept_status_counts[1]["Resolved"],
        electrical_rejected=dept_status_counts[1]["Rejected"],
        water_pending=dept_status_counts[2]["Pending"],
        water_progress=dept_status_counts[2]["In Progress"],
        water_resolved=dept_status_counts[2]["Resolved"],
        water_rejected=dept_status_counts[2]["Rejected"],
        pw_pending=dept_status_counts[3]["Pending"],
        pw_progress=dept_status_counts[3]["In Progress"],
        pw_resolved=dept_status_counts[3]["Resolved"],
        pw_rejected=dept_status_counts[3]["Rejected"],
        hc_pending=dept_status_counts[4]["Pending"],
        hc_progress=dept_status_counts[4]["In Progress"],
        hc_resolved=dept_status_counts[4]["Resolved"],
        hc_rejected=dept_status_counts[4]["Rejected"],
        total=total,
    )


# ------------------------------------
#        COMPLAINT ANALYTICS
# ------------------------------------
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

    labels = [r["department_name"] for r in rows]
    counts = [r["total"] for r in rows]

    daily_rows = query(
        """
        SELECT 
            TO_CHAR(created_at, 'DD Mon') AS day,
            DATE(created_at) AS day_order,
            COUNT(*) AS total
        FROM complaints
        GROUP BY day, day_order
        ORDER BY day_order
        """,
        fetchall=True,
    )

    trend_labels = [r["day"] for r in daily_rows]
    trend_counts = [r["total"] for r in daily_rows]

    status_rows = query(
        "SELECT status, COUNT(*) AS total FROM complaints GROUP BY status ORDER BY status",
        fetchall=True,
    )

    status_labels = [r["status"] for r in status_rows]
    status_counts = [r["total"] for r in status_rows]

    return render_template(
        "complaints_analytics.html",
        labels=labels,
        counts=counts,
        trend_labels=trend_labels,
        trend_counts=trend_counts,
        status_labels=status_labels,
        status_counts=status_counts,
    )


# ------------------------------------
#        EDIT COMPLAINT STATUS
# ------------------------------------
@bp.route("/complaints/<int:complaint_id>/status", methods=["GET", "POST"])
@login_required
def edit_status(complaint_id):
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST":
        new_status = request.form["status"]
        admin_comment = request.form["admin_comment"]

        old_status = query(
            "SELECT status FROM complaints WHERE complaint_id=%s",
            (complaint_id,),
            fetchone=True,
        )["status"]

        if new_status == old_status:
            flash("Status is unchanged!", "info")
            return redirect(url_for("admin.edit_status", complaint_id=complaint_id))

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

        staff_id = query(
            "SELECT staff_id FROM staff WHERE department_id=%s",
            (complaint_data["department_id"],),
            fetchone=True,
        )[0]

        # Send user email
        send_notification(
            to=complaint_data["email"],
            subject="Complaint Status Updated",
            body=(
                f"Hello {complaint_data['username']},\n\n"
                f"Your complaint '{complaint_data['title']}' status changed.\n"
                f"Old: {old_status}\nNew: {new_status}\n\nRegards,\nAdmin Team"
            ),
        )

        # Update DB
        if new_status == "In Progress":
            query(
                """
                UPDATE complaints 
                SET status=%s, assigned_to=%s, admin_comment=%s, assigned_at=NOW()
                WHERE complaint_id=%s
                """,
                (new_status, staff_id, admin_comment, complaint_id),
                commit=True,
            )

        elif new_status == "Rejected":
            query(
                """
                UPDATE complaints
                SET status=%s, assigned_to=NULL, assigned_at=NULL, admin_comment=%s
                WHERE complaint_id=%s
                """,
                (new_status, admin_comment, complaint_id),
                commit=True,
            )

        elif new_status == "Resolved":
            query(
                """
                UPDATE complaints
                SET status=%s, assigned_to=NULL, assigned_at=NULL, resolved_at=NOW(), admin_comment=%s
                WHERE complaint_id=%s
                """,
                (new_status, admin_comment, complaint_id),
                commit=True,
            )

        flash("Status updated successfully!", "success")
        return redirect(url_for("admin.admin_complaints"))

    comp = query(
        "SELECT * FROM complaints WHERE complaint_id=%s",
        (complaint_id,),
        fetchone=True,
    )

    return render_template("admin_edit_status.html", complaint=comp)


# ------------------------------------
#           ADD COMMENT
# ------------------------------------
@bp.route("/complaints/<int:complaint_id>/add_comment", methods=["POST"])
@login_required
def add_comment(complaint_id):
    if not current_user.is_admin:
        abort(403)

    admin_comment = request.form["admin_comment"].strip()

    query(
        "UPDATE complaints SET admin_comment=%s WHERE complaint_id=%s",
        (admin_comment, complaint_id),
        commit=True,
    )

    flash("Comment updated successfully", "success")
    return redirect(url_for("admin.admin_complaints"))

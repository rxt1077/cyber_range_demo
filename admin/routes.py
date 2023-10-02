from datetime import datetime, timezone

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    abort,
)
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt

import db
from admin.users import User, ROLE_ADMIN, ROLE_USER
from admin.forms import LoginForm, ManageProfileForm, EditUserForm, AddUserForm

admin_bp = Blueprint("admin", __name__, template_folder="templates")

DURATION = 60  # how many minutes to keep a user logged in


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """This endpoint allows a user to log in"""

    form = LoginForm()
    notification = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = db.get_connection()
        user_row = db.get_user_by_name(conn, username)

        #TODO: What if they don't exist?

        user_id = user_row["id"]
        name = user_row["name"]
        pw_hash = user_row["password"]
        role = user_row["role"]

        bcrypt = Bcrypt(current_app)
        if bcrypt.check_password_hash(pw_hash, password):
            db.set_auto_logout(conn, user_id, DURATION)
            conn.commit()
            conn.close()
            user = User(
                user_id=user_id, name=name, role=role, authenticated=True, active=True
            )
            login_user(user)
            return redirect(url_for("main.index"))

        conn.close()

        notification = "Invalid username or password"

    return render_template("login.html", form=form, notification=notification)


@admin_bp.route("/manage_profile", methods=["GET", "POST"])
@login_required
def manage_profile():
    """This endpoint allows a user to change their password or to
    manually log out"""

    form = ManageProfileForm()
    notification = None

    if form.logout.data:
        conn = db.get_connection()
        db.clear_auto_logout(conn, current_user.user_id)
        conn.commit()
        conn.close()
        logout_user()
        return redirect(url_for("admin.login"))

    if form.validate_on_submit():
        conn = db.get_connection()
        bcrypt = Bcrypt(current_app)
        password = form.password.data
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        db.update_user_password(conn, current_user.user_id, pw_hash)
        conn.commit()
        conn.close()
        notification = "Profile updated successfully"

    return render_template("manage_profile.html", form=form, notification=notification)


@admin_bp.route("/edit_user", methods=["GET"])
@login_required
def edit_user_get():
    if current_user.role != ROLE_ADMIN:
        abort(403)

    user_id = request.args.get("id")

    conn = db.get_connection()
    user = db.get_user(conn, user_id)
    conn.close()

    form = EditUserForm(
        username=user["name"],
        role=user["role"],
        time_remaining=user["time_remaining"],
        user_id=user_id,
    )

    return render_template("edit_user.html", form=form)


@admin_bp.route("/edit_user", methods=["POST"])
@login_required
def edit_user_post():
    if current_user.role != ROLE_ADMIN:
        abort(403)

    form = EditUserForm()
    if form.validate():
        user_id = form.user_id.data
        username = form.username.data
        password = form.password.data
        role = form.role.data
        time_remaining = form.time_remaining.data

        conn = db.get_connection()

        if form.logout.data:
            db.clear_auto_logout(conn, user_id)
        elif form.delete.data:
            db.del_user(conn, user_id)
        else:
            if password:
                bcrypt = Bcrypt(current_app)
                pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
                db.update_user_password(conn, user_id, pw_hash)
            if time_remaining:
                db.set_auto_logout(conn, user_id, time_remaining)
            db.update_user(conn, user_id, username, role)

        conn.commit()
        conn.close()

        return redirect(url_for("admin.manage_users"))

    # re-render the edit_user.html template if we have validation errors
    return render_template("edit_user.html", form=form)


@admin_bp.route("/manage_users", methods=["GET", "POST"])
@login_required
def manage_users():
    """This endpoint has a form to add users and a list of current users.
    POSTS to this endpoint are for add user operations."""

    if current_user.role != ROLE_ADMIN:
        abort(403)

    conn = db.get_connection()

    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if form.role.data == "ADMIN":
            role = ROLE_ADMIN
        else:
            role = ROLE_USER

        if db.get_user_by_name(conn, username):
            form.username.errors.append("Username already in use")
        else:
            bcrypt = Bcrypt(current_app)
            pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            db.add_user(conn, username, pw_hash, role)
            conn.commit()
            conn.close()

            return redirect(url_for("admin.manage_users"))

    user_row = db.get_all_users(conn)
    conn.close()

    user_list = []
    for user in user_row:
        # create friendly text for role
        if user["role"] == ROLE_ADMIN:
            role = "Administrator"
        else:
            role = "User"

        # determine if they are logged in or not and time remaining
        time_remaining = user["time_remaining"]
        if time_remaining:
            logged_in = "Yes"
        else:
            logged_in = "No"
            time_remaining = "None"

        user_list.append(
            {
                "id": user["id"],
                "name": user["name"],
                "role": role,
                "logged_in": logged_in,
                "time_remaining": time_remaining,
            }
        )

    return render_template("manage_users.html", form=form, user_list=user_list)

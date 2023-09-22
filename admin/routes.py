from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, current_app, abort
from flask_login import login_required, login_user, current_user
from flask_bcrypt import Bcrypt

import db
from admin.util import User, ROLE_ADMIN, ROLE_USER

admin_bp = Blueprint('admin', __name__, template_folder='templates')

DURATION = 60 # how many minutes to keep a user logged in for

@admin_bp.route('/login')
def login():
    return render_template('login.html')

@admin_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = db.get_connection()
    user_row = db.get_user_by_name(conn, username)

    if user_row:
        bcrypt = Bcrypt(current_app)
        user_id = user_row['id']
        name = user_row['name']
        pw_hash = user_row['password']
        role = user_row['role']
        if bcrypt.check_password_hash(pw_hash, password):
            db.set_auto_logout(conn, user_id, DURATION)
            conn.commit()
            conn.close()
            user = User(user_id=user_id, name=name, role=role, authenticated=True, active=True)
            login_user(user)
            return redirect(url_for('main.index'))

    conn.close()
    return render_template('login_error.html')

@admin_bp.route('/logout')
@login_required
def logout():
    conn = db.get_connection()
    db.clear_auto_logout(conn, current_user.user_id)
    conn.commit()
    conn.close()
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/add_user', methods=['POST'])
@login_required
def add_user_post():
    if current_user.role != ROLE_ADMIN:
        abort(403)

    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    if role == "ADMIN":
        role = ROLE_ADMIN
    else:
        role = ROLE_USER

    print(username, password, role)
    conn = db.get_connection()
    db.add_user(conn, username, password, role)
    conn.commit()
    conn.close()

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if current_user.role != ROLE_ADMIN:
        abort(403)

    user_id = request.form.get('id')

    conn = db.get_connection()
    db.del_user(conn, user_id)
    conn.commit()
    conn.close()

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/logout_user', methods=['POST'])
@login_required
def logout_user():
    if current_user.role != ROLE_ADMIN:
        abort(403)

    user_id = int(request.form.get('id'))

    conn = db.get_connection()
    db.clear_auto_logout(conn, user_id)
    conn.commit()
    conn.close()

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != ROLE_ADMIN:
        abort(403)

    conn = db.get_connection()
    user_row = db.get_all_users(conn)
    conn.close()

    user_list = []
    for user in user_row:
        # create friendly text for role
        if user['role'] == ROLE_ADMIN:
            role = "Administrator"
        else:
            role = "User"

        # determine if they are logged in or not and time remaining
        time_remaining = user['time_remaining']
        if time_remaining:
            logged_in = "Yes"
        else:
            logged_in = "No"
            time_remaining = "None"

        user_list.append({
            'id': user['id'],
            'name': user['name'],
            'role': role,
            'logged_in': logged_in,
            'time_remaining': time_remaining,
        })

    return render_template('manage_users.html', user_list=user_list)

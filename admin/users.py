from flask_login import logout_user

import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User():
    def __init__(self, user_id=None, name=None, authenticated=False, active=False, anonymous=False, role=ROLE_USER, time_remaining=None, active_challenge=None):
        self.user_id = user_id
        self.name = name
        self.authenticated = authenticated
        self.active = active
        self.anonymous = anonymous
        self.role = role
        self.time_remaining = time_remaining
        self.active_challenge = active_challenge

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        return self.user_id

def load_user(user_id):
    conn = db.get_connection()
    user = db.get_user(conn, user_id)

    if user:
        user_id = user['id']
        name = user['name']
        role = user['role']
        time_remaining = user['time_remaining']
        # users that have NULL time remaining are logged out
        if time_remaining:
            challenge = db.get_challenge(conn, user_id)
            if challenge:
                active_challenge=challenge['name']
            else:
                active_challenge=None
            print(f"active_challenge={active_challenge}")
            return User(user_id=user_id, name=name, role=role, time_remaining=time_remaining, active_challenge=active_challenge) 
    conn.close()
    return None

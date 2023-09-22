import os

from flask import Flask
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

import db
from admin.util import load_user, ROLE_ADMIN
from scheduler import cleanup
from main.routes import main_bp
from admin.routes import admin_bp
from challenges.routes import challenges_bp

wookie = 7

def create_app():
    # load environment variables from .env
    load_dotenv()

    # set up Flask
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')

    # set up Flask-Bcrypt
    bcrypt = Bcrypt(app)

    # set up Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    login_manager.login_view = 'admin.login'

    # create the DB if it isn't there
    if not os.path.isfile(db.DB_FILE):
        print(f"{db.DB_FILE} not found, initializing a new database")
        db_conn = db.get_connection()
        db.init(db_conn)
        # add a default admin
        db.add_user(db_conn, 'admin', bcrypt.generate_password_hash(os.getenv('DEFAULT_ADMIN_PASSWORD')).decode('utf-8'), ROLE_ADMIN)
        db_conn.commit()
        db_conn.close()

    # schedule cleanup() to run every minute
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup, trigger="interval", seconds=60)
    scheduler.start()

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(challenges_bp)

    return app

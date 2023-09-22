"""Main routes for this app"""

from flask import render_template, Blueprint
from flask_login import login_required

import db

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='') 

@main_bp.route("/")
@login_required
def index():
    """An landing page talking about what this project is"""

    return render_template("index.html")

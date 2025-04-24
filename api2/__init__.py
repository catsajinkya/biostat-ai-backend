from flask import Blueprint
from .routes import summarize_history

api2_bp = Blueprint('api2', __name__)
api2_bp.add_url_rule('/summarize_history', view_func=summarize_history, methods=['POST'])

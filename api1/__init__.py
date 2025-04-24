from flask import Blueprint
from .routes import summarize_report

api1_bp = Blueprint('api1', __name__)
api1_bp.add_url_rule('/summarize_report', view_func=summarize_report, methods=['POST'])

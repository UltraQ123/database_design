from flask import Blueprint
forbidden_blue = Blueprint('forbidden', __name__,template_folder="templates", static_folder='static')
from . import routes

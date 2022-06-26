from flask import Blueprint
api_blue = Blueprint('api', __name__,template_folder="templates", static_folder='static')
from . import routes

from flask import Blueprint
card_blue = Blueprint('card', __name__,template_folder="templates", static_folder='static')
from . import routes

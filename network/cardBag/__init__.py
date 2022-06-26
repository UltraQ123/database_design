from flask import Blueprint
cardBag_blue = Blueprint('cardBag', __name__,template_folder="templates", static_folder='static')
from . import routes

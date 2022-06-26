from flask import Blueprint
cardSet_blue = Blueprint('cardSet', __name__,template_folder="templates", static_folder='static')
from . import routes

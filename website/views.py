from flask import Blueprint, render_template
from flask_login import current_user
from .models import Product
from .recommendations import get_recommendations

views = Blueprint('views', __name__)

@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True).all()

    recommended = []
    if current_user.is_authenticated:
        recommended = get_recommendations(current_user.id)
        print("RECOMMENDED:", recommended)  # Add this for debugging

    return render_template('home.html', items=items, recommended=recommended)

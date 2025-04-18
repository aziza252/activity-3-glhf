from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from .models import Order, Product
from . import db

kitchen = Blueprint('kitchen', __name__)

@kitchen.route('/kitchen-orders')
@login_required
def kitchen_orders():
    if current_user.id != 2:  # Assuming ID 2 is kitchen staff
        return render_template('404.html')

    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('kitchen-orders.html', orders=orders)

@kitchen.route('/update-kitchen-status/<int:order_id>', methods=['POST'])
@login_required
def update_kitchen_status(order_id):
    if current_user.id != 2:
        return render_template('404.html')

    new_status = request.form.get("status")
    order = Order.query.get(order_id)

    if order:
        order.kitchen_status = new_status
        db.session.commit()
        flash(f"Order #{order.id} status updated to {new_status}")
    else:
        flash("Order not found.")

    return redirect('/kitchen-orders')

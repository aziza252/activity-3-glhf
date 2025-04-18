from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from .models import Cart, Product, Order
from . import db
from datetime import datetime
from collections import Counter
from .models import Favourite, Review


menu = Blueprint('menu', __name__)

@menu.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

@menu.route('/menu', methods=['GET'])
def show_menu():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(Product.product_name.ilike(f"%{search_query}%")).all()
    else:
        products = Product.query.all()

    return render_template('menu.html', products=products, search_query=search_query)

@menu.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    customization = request.form.get('customizations', '')

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.")
        return redirect('/menu')

    new_cart_item = Cart(
        quantity=quantity,
        customization=customization,
        customer_link=current_user.id,
        product_link=product_id
    )

    db.session.add(new_cart_item)
    db.session.commit()
    flash(f"{product.product_name} added to cart!")
    return redirect('/menu')

@menu.route('/promo')
def promotions():
    items = Product.query.filter_by(flash_sale=True).all()
    return render_template('promotions.html', items=items)


@menu.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(customer_link=current_user.id).all()

    total = sum(item.quantity * item.product.current_price for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total)

# Add to favourites
@menu.route('/favourite/<int:product_id>', methods=['POST'])
@login_required
def add_favourite(product_id):
    existing = Favourite.query.filter_by(customer_link=current_user.id, product_link=product_id).first()
    if not existing:
        fav = Favourite(customer_link=current_user.id, product_link=product_id)
        db.session.add(fav)
        db.session.commit()
        flash("Added to favourites!")
    else:
        flash("Already in favourites.")
    return redirect('/menu')

# View favourites
@menu.route('/favourites')
@login_required
def show_favourites():
    favs = Favourite.query.filter_by(customer_link=current_user.id).all()
    return render_template('favourites.html', favourites=favs)

@menu.route('/remove-favourite/<int:product_id>', methods=['POST'])
@login_required
def remove_favourite(product_id):
    fav = Favourite.query.filter_by(customer_link=current_user.id, product_link=product_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash("Removed from favourites.")
    else:
        flash("Item not found in favourites.")
    return redirect('/favourites')

@menu.route('/remove-from-cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get(cart_id)
    if cart_item and cart_item.customer_link == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.')
    else:
        flash('Unauthorized or item not found.')
    return redirect('/cart')

@menu.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(customer_link=current_user.id).all()
    total = sum(item.quantity * item.product.current_price for item in cart_items)

    if not cart_items:
        flash("Your cart is empty.")
        return redirect('/cart')

    if request.method == 'POST':
        for item in cart_items:
            new_order = Order(
                quantity=item.quantity,
                price=item.quantity * item.product.current_price,
                status='Completed',
                payment_id=f'pay_{datetime.utcnow().timestamp()}',
                customer_link=current_user.id,
                product_link=item.product.id,
                customization=item.customization
            )
            db.session.add(new_order)
            db.session.delete(item)
        
        db.session.commit()
        flash("Checkout successful! Thank you for your order.")
        return redirect('/')

    return render_template('checkout.html', cart_items=cart_items, total=total)

@menu.route('/order-history')
@login_required
def order_history():
    orders = Order.query.filter_by(customer_link=current_user.id).order_by(Order.id.desc()).all()
    return render_template('order_history.html', orders=orders)

@menu.route('/submit-review', methods=['POST'])
def submit_review():
    name = request.form.get('name')
    email = request.form.get('email')
    comment = request.form.get('comments')

    if name and email and comment:
        new_review = Review(name=name, email=email, comment=comment)
        db.session.add(new_review)
        db.session.commit()
        flash("Thanks for your message! Our team will review it shortly.")
    else:
        flash("Please fill in all fields before submitting.")

    return redirect('/contact-us')

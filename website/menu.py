from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from .models import Product, Cart, Favourite
from . import db

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

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.")
        return redirect('/menu')

    existing_item = Cart.query.filter_by(customer_link=current_user.id, product_link=product_id).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_cart_item = Cart(
            quantity=quantity,
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


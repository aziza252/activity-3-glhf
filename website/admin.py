from flask import Blueprint, render_template, flash, send_from_directory, redirect, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import ShopItemsForm
from .models import Product, Review, Order, Customer
from . import db
import os
import csv

admin = Blueprint('admin', __name__)

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)

            media_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))
            if not os.path.exists(media_folder):
                os.makedirs(media_folder)

            file_path = os.path.join(media_folder, file_name)
            file.save(file_path)
            relative_path = f'./media/{file_name}'

            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                flash_sale=flash_sale,
                product_picture=relative_path
            )

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} has been added to the shop')
                print("Product added")
            except Exception as e:
                print(e)
                flash('Item Not Added')

        return render_template('add-shop-items.html', form=form)
    return render_template('404.html')

@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop-items.html', items=items)
    return render_template('404.html')

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)

        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)

            media_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))
            if not os.path.exists(media_folder):
                os.makedirs(media_folder)

            file_path = os.path.join(media_folder, file_name)
            file.save(file_path)
            relative_path = f'./media/{file_name}'

            try:
                Product.query.filter_by(id=item_id).update(dict(
                    product_name=product_name,
                    current_price=current_price,
                    previous_price=previous_price,
                    in_stock=in_stock,
                    flash_sale=flash_sale,
                    product_picture=relative_path
                ))
                db.session.commit()
                flash(f'{product_name} has been updated')
                print("Product updated")
                return redirect('/shop-items')
            except Exception as e:
                print('Product not updated', e)
                flash('Item Not Updated')

        return render_template('update-item.html', form=form)
    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash(f'{item_to_delete.product_name} has been deleted')
            print("Product deleted")
        except Exception as e:
            print('Product not deleted', e)
            flash('Item Not Deleted')
        return redirect('/shop-items')
    return render_template('404.html')

@admin.route('/admin-reviews')
@login_required
def admin_reviews():
    if current_user.id == 1:
        reviews = Review.query.order_by(Review.date_submitted.desc()).all()
        return render_template('admin-reviews.html', reviews=reviews)
    return render_template('404.html')

@admin.route('/download-report')
@login_required
def download_report():
    if current_user.id != 1:
        return render_template('404.html')

    # Query and build all data inside the app context
    orders = Order.query.filter_by(status='Completed').all()
    data = [['Customer Name', 'Email', 'Product', 'Quantity', 'Price', 'Status', 'Payment ID']]

    for order in orders:
        customer = Customer.query.get(order.customer_link)
        product = Product.query.get(order.product_link)

        if customer and product:
            data.append([
                customer.username,
                customer.email,
                product.product_name,
                order.quantity,
                order.price,
                order.status,
                order.payment_id
            ])

    # Define the generator AFTER all DB access
    def generate():
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=order_report.csv"})


@admin.route('/delete-review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    if current_user.id == 1:
        review = Review.query.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()
            flash('Review deleted successfully.')
        else:
            flash('Review not found.')
        return redirect('/admin-reviews')
    return render_template('404.html')

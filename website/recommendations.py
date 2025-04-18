from .models import Order, Product
import random

def get_recommendations(customer_id):
    # Get product IDs the customer ordered
    order_product_ids = [order.product_link for order in Order.query.filter_by(customer_link=customer_id).all()]

    if order_product_ids:
        # Recommend based on past orders
        return Product.query.filter(Product.id.in_(order_product_ids)).limit(4).all()
    else:
        # Recommend flash sale or random products if no history
        products = Product.query.all()
        random.shuffle(products)
        return products[:4]

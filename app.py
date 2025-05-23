from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import requests

app = Flask(__name__)

# Configure server-side session storage
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_products():
    products_resp = requests.get("https://api.escuelajs.co/api/v1/products?limit=24")
    products = products_resp.json()
    return products

@app.route('/')
def home():
    # Clear cart once per session
    if not session.get('cart_cleared'):
        session['cart'] = {}
        session['cart_cleared'] = True

    products = get_products()
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template("index.html", title="Clothes", products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = session.get('cart', {})

    if request.method == 'POST':
        for product_id in list(cart.keys()):
            qty_str = request.form.get(f'quantity_{product_id}')
            if qty_str and qty_str.isdigit():
                qty = int(qty_str)
                if qty > 0:
                    cart[product_id] = qty
                else:
                    cart.pop(product_id)
        session['cart'] = cart
        return redirect(url_for('cart'))

    all_products = get_products()
    products_in_cart = []
    total = 0
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        product = next((p for p in all_products if p['id'] == pid), None)
        if product:
            product_copy = product.copy()
            product_copy['quantity'] = qty
            products_in_cart.append(product_copy)
            total += product['price'] * qty

    cart_count = sum(cart.values())

    return render_template("cart.html", products=products_in_cart, total=total, cart_count=cart_count)

@app.route('/place_order', methods=['POST'])
def place_order():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    address = request.form.get('address')
    card_number = request.form.get('card_number')
    expiry_date = request.form.get('expiry_date')
    cvv = request.form.get('cvv')

    # TODO: Process payment here (mocked/skipped)

    # Clear the cart after order is placed
    session['cart'] = {}

    # Simple confirmation message
    return f'''
        <h1>Thank you for your order, {full_name}!</h1>
        <p>A confirmation email will be sent to {email}.</p>
        <p>Your order will be shipped to: {address}</p>
        <a href="{url_for('home')}">Continue Shopping</a>
    '''

if __name__ == "__main__":
    app.run(debug=True)

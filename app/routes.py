from app import app
from flask import Flask, render_template, abort
 
PRODUCTS = {
    'coaching': {
        'name': 'Coaching Classes',
        'category': 'coaching',
        'price':'Starting at 1000',
    },
    'galaxy': {
        'name': 'Hostels',
        'category': 'Phones',
        'price':'Starting at 1500',
    },
    'ipad-air': {
        'name': 'Individual rooms/flats',
        'category': 'Tablets',
        'price':'Starting at 1500',
    },
    'ipad-mini': {
        'name': 'Examinee rooms',
        'category': 'Tablets',
        'price':'Starting at 2500'
    }
}
 
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', products=PRODUCTS)
 
@app.route('/product/<key>')
def product(key):
    product = PRODUCTS.get(key)
    if not product:
        abort(404)
    return render_template('product.html', product=product)

@app.route('/coaching')
def coaching():
    return render_template('coaching.html')


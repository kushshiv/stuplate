from app import app
from flask import Flask, render_template, abort
 
ITEMS = {
    'coaching': {
        'name': 'Coaching Classes',
        'category': 'coaching',
        'price':'Starting at 1000',
    },
    'hostels': {
        'name': 'Hostels',
        'category': 'Phones',
        'price':'Starting at 1500',
    },
    'rooms': {
        'name': 'Individual rooms/flats',
        'category': 'Tablets',
        'price':'Starting at 1500',
    },
    'examinee': {
        'name': 'Examinee rooms',
        'category': 'Tablets',
        'price':'Starting at 2500'
    }
}
 
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', items=ITEMS)
 
@app.route('/item/<key>')
def item(key):
    item = ITEMS.get(key)
    if not item:
        abort(404)
    #return render_template('item.html', item=item)
    return render_template(key + '.html', item=item)


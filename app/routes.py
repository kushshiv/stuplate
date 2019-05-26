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
 
productsList = {
    'coaching1': {
        'id': '100',
        'name': 'A Coaching Classes',
        'category': 'IIT',
	'location': 'Patna',
        'price':'Starting at 1000',
    },  
    'coaching2': {
        'id': '101',
        'name': 'B Coaching Classes',
        'category': 'IIT',
        'location': 'Patna',
        'price':'Starting at 1500',
    },
    'coaching3': {
        'id': '103',
        'name': 'C Coaching Classes',
        'category': 'GATE',
        'location': 'Mumbai',
        'price':'Starting at 1600',
    },
    'coaching4': {
        'id': '104',
        'name': 'D Coaching Classes',
        'category': 'UPSC',
        'location': 'Pune',
        'price':'Starting at 100',
    },
    'coaching5': {
        'id': '105',
        'name': 'E Coaching Classes',
        'category': 'UPSC',
        'location': 'Pune',
        'price':'Starting at 2500'
    }
}


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', items=ITEMS)
 
@app.route('/item/<key>')
def item(key):
    item = productsList.get(key)
    if not item:
        abort(404)
    return render_template('item.html', item=item)

@app.route('/productList')
def productList():
    return render_template('productList.html', productList=productsList)

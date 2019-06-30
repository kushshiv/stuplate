from app import app
from flask import Flask, render_template, abort, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from random import randint
from time import strftime
  
 
ITEMS = {
    'coaching': {
        'name': 'Coaching Classes',
        'category': 'coaching',
        'price':'Starting at 1000',
    },
#    'hostels': {
#        'name': 'Hostels',
#        'category': 'Phones',
#        'price':'Starting at 1500',
#    },
#    'rooms': {
#        'name': 'Individual rooms/flats',
#        'category': 'Tablets',
#        'price':'Starting at 1500',
#    },
#    'examinee': {
#        'name': 'Examinee rooms',
#        'category': 'Tablets',
#        'price':'Starting at 2500'
#    }
}
 
productsList = {
    'coaching1': {
        'id': '100',
        'name': 'A Coaching Classes',
        'category': 'IIT',
	'location': 'Patna',
	'overview' : 'A Coaching Classes is leading coaching institute in Patna for IIT JEE exam. Best IIT JEE Coaching in Patna.',
        'price':'Starting at 1000',
    },  
    'coaching2': {
        'id': '101',
        'name': 'B Coaching Classes',
        'category': 'IIT',
        'location': 'Patna',
	'overview' : 'B Coaching Classes is leading coaching institute in Patna for IIT JEE exam. Best IIT JEE Coaching in Patna.',
        'price':'Starting at 1500',
    },
    'coaching3': {
        'id': '103',
        'name': 'C Coaching Classes',
        'category': 'GATE',
        'location': 'Mumbai',
	'overview' : 'C Coaching Classes is leading coaching institute in Mumbai for GATE exam.',
        'price':'Starting at 1600',
    },
    'coaching4': {
        'id': '104',
        'name': 'D Coaching Classes',
        'category': 'UPSC',
        'location': 'Pune',
	'overview' : 'D Coaching Classes is leading coaching institute in Pune for UPSC exam. Best UPSC Coaching in Pune.',
        'price':'Starting at 100',
    },
    'coaching5': {
        'id': '105',
        'name': 'E Coaching Classes',
        'category': 'UPSC',
        'location': 'Pune',
	'overview' : 'E Coaching Classes is leading coaching institute in Pune for UPSC exam.',
        'price':'Starting at 2500'
    }
}


class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(name, email):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Name={}, Email={} \n'.format(timestamp, name, email))
    data.close()



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

@app.route("/CoachingInput", methods=['GET', 'POST'])
def CoachingInput ():
    form = ReusableForm(request.form)

    #print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['email']
        mobile=request.form['mobile']
        password=request.form['password']
        CoachingType=request.form['Coaching Type']

        if form.validate():
            write_to_disk(name, email)
            flash('Hello: {}'.format(name))

        else:
            flash('Error: All Fields are Required')

    return render_template('CoachingInput.html', form=form)

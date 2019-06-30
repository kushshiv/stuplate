from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    surname = TextField('Surname:', validators=[validators.required()])

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(name, surname, email):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Name={}, Surname={}, Email={} \n'.format(timestamp, name, surname, email))
    data.close()




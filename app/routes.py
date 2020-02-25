import os
import fnmatch
from app import app
from time import strftime
from random import randint
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from flask import Flask, render_template, abort, flash, request, redirect, url_for, make_response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Newsticker, CoachingClass, CoachingTeachers, StudentDetails, StudentCoachingRelation, CoachingBatches
from werkzeug.urls import url_parse
from app import db
from werkzeug import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_mail import Mail, Message
from flask_mail import Mail
from wtforms.fields.html5 import DateField
from wtforms import widgets
from wtforms.widgets import html_params, HTMLString
import pdfkit
from sqlalchemy import func
from threading import Thread

  
 
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

# Configure the image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)
mail = Mail(app)

cityList=[]
#city_file = os.path.join(basedir, 'static/citylist.txt')
city_file = os.path.join(app.config['FILE_FOLDER'], 'citylist.txt')
with open(city_file) as myfile:
   citydata = myfile.readlines()
   for line in citydata:
      cd = line.strip('\n')
      cityList.append(tuple([cd,cd]))


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


class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #usertype = SelectField('User Type', choices = [('Student'), ('Coaching Class')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    usertype = SelectField('User Type', choices = [('Student', 'Student')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AdminRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    usertype = SelectField('User Type', choices = [('Admin', 'Admin'), ('Coaching', 'Coaching'), ('Student', 'Student')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class UpdateNewsForm(FlaskForm):
    news = StringField('News', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CoachingRegistrationForm(FlaskForm):
    coachingname = StringField('coachingname', validators=[validators.required()])
    coachingcontact = StringField('Contact', validators=[validators.required()])
    coachingemail = StringField('Email', validators=[validators.required()])
    coachingabout = TextAreaField('About', validators=[validators.required()])
    coachingcategory = SelectField('Category', choices = [('Academic', 'Academic'), ('Entrance', 'Entrance'), ('Competition', 'Competition'), ('ComputerClasses', 'Computer Classes'), ('SpokenEnglishClasses', 'Spoken English Classes'), ('Others', 'Others')], validators=[validators.required()])
    coachinglocation = SelectField('Location', choices = cityList, validators=[validators.required()])
    teachersname = StringField('Teachers Name', validators=[validators.required()])
    teachersqualification = StringField('Teachers Qualification', validators=[validators.required()])
    teacherssubject = StringField('Teachers Subject', validators=[validators.required()])
    teachersexperience = StringField('Teachers Experience', validators=[validators.required()])
    teachers_image = FileField('Teachers Image', validators=[validators.required()])
    submit_teachers = SubmitField('Submit')

class CoachingTeachersEditForm(FlaskForm):
    teachersname = StringField('Teachers Name', validators=[validators.required()])
    teachersqualification = StringField('Teachers Qualification', validators=[validators.required()])
    teacherssubject = StringField('Teachers Subject', validators=[validators.required()])
    teachersexperience = StringField('Teachers Experience', validators=[validators.required()])
    teachers_image = FileField('Teachers Image', validators=[validators.required()])
    submit_teachers = SubmitField('Submit')

class StudentRegistrationForm(FlaskForm):
    studentname = StringField('Full Name', validators=[validators.required()])
    studentcontact = StringField('Contact', validators=[validators.required()])
    studentgender = SelectField('Gender', choices = [('Male', 'Male'), ('Female', 'Female')], validators=[validators.required()])
    studentaddress = StringField('Full Address', validators=[validators.required()])
    studentfathersname = StringField('Fathers Name', validators=[validators.required()])
    studentqualification = StringField('Qualification', validators=[validators.required()])
    submit = SubmitField('Submit')

class StudentCoachingRelationForm(FlaskForm):
    student_id = StringField('Student ID', validators=[validators.required()])
    CoachingBatch = StringField('Batch ID', validators=[validators.required()])
    CoachingSubject = StringField('Description/Subject', validators=[validators.required()])
    CoachingPaidAmount = StringField('Paid Amount', validators=[validators.required()])
    submit = SubmitField('Tag')

class EditNewsForm(FlaskForm):
    news = StringField('News', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class EditCoachingForm(FlaskForm):
    coachingname = StringField('coachingname', validators=[DataRequired()])
    coachingcontact = StringField('Contact', validators=[DataRequired()])
    coachingemail = StringField('Email', validators=[DataRequired(), Email()])
    coachingabout = TextAreaField('About', validators=[DataRequired()])
    coachingcategory = SelectField('Category', choices = [('Academic', 'Academic'), ('Entrance', 'Entrance'), ('Competition', 'Competition'), ('ComputerClasses', 'Computer Classes'), ('SpokenEnglishClasses', 'Spoken English Classes'), ('Others', 'Others')], validators=[DataRequired()])
    coachinglocation = SelectField('Location', choices = cityList, validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateCoachingFeesForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    CoachingBatch = StringField('Batch ID', validators=[DataRequired()])
    CoachingSubject = StringField('Subject', validators=[DataRequired()])
    CoachingPaidAmount = StringField('Total Amount Paid', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ContactMailForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=0, max=140)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    comments = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CoachingBatchesForm(FlaskForm):
    batchname = StringField('Batch Name', validators=[Length(min=0, max=140)])
    batchdescription = TextAreaField('Batch Description', validators=[Length(min=0, max=140)])
    batchstartdate = DateField('Start Date')
    batchenddate = DateField('End Date')
    batchfees = StringField('Batch Fees', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
@app.route('/home')
def home():
    news = Newsticker.query.all()
    coachings = CoachingClass.query.all()
    coachingnames = [r.coachingname for r in coachings ]
    files = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/home")), '*.jpg')
    return render_template('home.html', items=ITEMS, news=news, files=files, coachings=coachings,coachingnames=coachingnames)
 
@app.route('/item/<key>')
def item(key):
    #item = productsList.get(key)
    item = CoachingClass.query.get(key)
    #teachers = CoachingTeachers.query.filter_by(user_id2=current_user.id).all()
    coachingUserId = CoachingClass.query.filter_by(coachingid=str(key)).first_or_404()
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(coachingUserId.user_id),batchIsActive='YES')
    teachers = CoachingTeachers.query.filter_by(user_id2=coachingUserId.user_id).all()
    CoachingClassSliderimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' +'CoachingClassSliderfile*' + '_' + '*.*')
    CoachingClassAchievementimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' +'CoachingClassAchievementfile' + '_' + '*.*')
    CoachingClassResultsimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' +'CoachingClassResultsfile' + '_' + '*.*')
    if not item:
        abort(404)
    return render_template('item.html', item=item, CoachingClassSliderimages=CoachingClassSliderimages, CoachingClassAchievementimages=CoachingClassAchievementimages, CoachingClassResultsimages=CoachingClassResultsimages, teachers=teachers, coachingbatches=coachingbatches)

@app.route('/productList')
def productList():
    page = request.args.get('page', 1, type=int)
    productsList = CoachingClass.query.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('productList', page=productsList.next_num) \
        if productsList.has_next else None
    prev_url = url_for('productList', page=productsList.prev_num) \
        if productsList.has_prev else None
    return render_template('productList.html', productList=productsList.items, next_url=next_url, prev_url=prev_url)
    #productsList = CoachingClass.query.all()
    #return render_template('productList.html', productList=productsList)

@app.route("/coachingregistration", methods=['GET', 'POST'])
def coachingregistration():
    form = CoachingRegistrationForm()
    if request.form.get('submit_teachers') == 'Submit':
        coaching_id = current_user.id
        filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
        for file in filefield:
            f = request.files[file]
            f.filename = str(coaching_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
        filename1 = secure_filename(form.teachers_image.data.filename)
        form.teachers_image.data.save(app.config['UPLOAD_TEACHERS_FOLDER'] + filename1)
        url = images.url(filename1)
        coachingteachers = CoachingTeachers(teachersname=form.teachersname.data, teachersqualification=form.teachersqualification.data, teacherssubject=form.teacherssubject.data, teachersexperience=form.teachersexperience.data, image_filename=filename1, image_url=url, teacher=current_user)
        db.session.add(coachingteachers)
        db.session.commit()
        regCoaching = CoachingClass(coachingname=form.coachingname.data, coachingcontact=form.coachingcontact.data, coachingemail=form.coachingemail.data, coachingpassword_hash='sjkfjlsdjflasdfjkldjflksdfjksdjlfsd', coachingabout=form.coachingabout.data, coachingcategory=form.coachingcategory.data, coachinglocation=form.coachinglocation.data, author=current_user)
        db.session.add(regCoaching)
        db.session.commit()
        return redirect(url_for('productList'))
    return render_template('coachingregistration.html', title='Register Coaching', form=form )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            flash('Logged in Successfully')
            if current_user.usertype == 'Admin':
                next_page = url_for('home')
            elif current_user.usertype == 'Coaching':
                try:
                    coachingID = current_user.coachingclass.all()[0].coachingid
                except IndexError:
                    coachingID = ''
                if coachingID:
                    next_page = url_for('item' , key=coachingID)
                else:
                    next_page = url_for('coachingregistration')
            elif current_user.usertype == 'Student':
                try:
                    studentID = current_user.studentdetails.all()[0].studentid
                except IndexError:
                    studentID = ''
                if studentID:
                    next_page = url_for('home')
                else:
                    next_page = url_for('studentregistration')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/StudentDescrition')
def StudentDescrition():
    # ...
    return render_template("StudentDescrition.html", title='Home Page', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    formType = 'NonAdmin'
    if current_user.is_authenticated:
        if current_user.usertype == 'Admin':
            formType = 'Admin'
        else:
            return redirect(url_for('home'))
    if formType == 'Admin':
        form = AdminRegistrationForm()
    else:
        form = RegistrationForm()
    if form.validate_on_submit():
        #if form.usertype.data == 'Coaching':
        user = User(username=form.email.data, email=form.email.data, usertype=form.usertype.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if formType == 'Admin':
            flash('User Login has been created. Please logout and login with registered user to check.')
            return redirect(url_for('login'))
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/underMaintenance')
def underMaintenance():
    return render_template('underMaintenance.html')

@app.route("/updateNewsFeed", methods=['GET', 'POST'])
def updateNewsFeed():
    currentNews = Newsticker.query.all()
    form = UpdateNewsForm()
    if form.validate_on_submit():
        newNews = Newsticker(news=form.news.data)
        db.session.add(newNews)
        db.session.commit()
        flash('Congratulations, News live now!')
        return redirect(url_for('updateNewsFeed'))
    return render_template('updateNewsFeed.html', title='Update News', form=form, currentNews=currentNews)

@app.route('/mycoaching/<key>')
def mycoaching(key):
    #item = productsList.get(key)
    mycoaching = CoachingClass.query.get(key)
    #images = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*.jpg')
    if not mycoaching:
        abort(404)
    return render_template('mycoaching.html', mycoaching=mycoaching)

@app.route('/edit_news/<key>', methods=['GET', 'POST'])
def edit_news(key):
    form = EditNewsForm()
    if form.validate_on_submit():
        News = Newsticker.query.get(key)
        News.news = form.news.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('updateNewsFeed'))
    elif request.method == 'GET':
        News = Newsticker.query.get(key)
        form.news.data = News.news
    return render_template('edit_news.html', title='Edit News',
                           form=form)

@app.route('/edit_coaching/<key>', methods=['GET', 'POST'])
def edit_coaching(key):
    form = EditCoachingForm()
    mycoaching = CoachingClass.query.get(key)
    coaching_id = current_user.id
    coachingUserId = CoachingClass.query.filter_by(coachingid=str(key)).first_or_404()
    teachers = CoachingTeachers.query.filter_by(user_id2=coachingUserId.user_id).all()
    coachingSlideImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' + 'CoachingClassSliderfile*' + '*.*')
    coachingAchievementImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' + 'CoachingClassAchievementfile*' + '*.*')
    coachingResultsImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' + 'CoachingClassResultsfile*' + '*.*')
    if request.form.get('submit') == 'submit_images':
        coaching_id = current_user.id
        filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
        for file in filefield:
            f = request.files[file]
            if f.filename:
                f.filename = str(coachingUserId.user_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
        return render_template('mycoaching.html', mycoaching=mycoaching)
    elif form.validate_on_submit():
        Coaching = CoachingClass.query.get(key)
        Coaching.coachingname = form.coachingname.data
        Coaching.coachingcontact = form.coachingcontact.data
        Coaching.coachingemail = form.coachingemail.data
        Coaching.coachingabout = form.coachingabout.data
        Coaching.coachingcategory = form.coachingcategory.data 
        Coaching.coachinglocation = form.coachinglocation.data 
        db.session.commit()
        flash('Your changes have been saved.')
        return render_template('mycoaching.html', mycoaching=mycoaching)
    elif request.method == 'GET':
        Coaching = CoachingClass.query.get(key)
        form.coachingname.data = Coaching.coachingname
        form.coachingcontact.data = Coaching.coachingcontact
        form.coachingemail.data = Coaching.coachingemail
        form.coachingabout.data = Coaching.coachingabout
        form.coachingcategory.data = Coaching.coachingcategory
        form.coachinglocation.data = Coaching.coachinglocation
    return render_template('edit_coaching.html', title='Edit Coaching',
                           form=form, coachingSlideImg_list=coachingSlideImg_list, coachingAchievementImg_list=coachingAchievementImg_list, coachingResultsImg_list=coachingResultsImg_list,teachers=teachers)

#def edit_coaching(key):
#    form = EditCoachingForm()
#    mycoaching = CoachingClass.query.get(key)
#    coaching_id = current_user.id
#    coachingUserId = CoachingClass.query.filter_by(coachingid=str(key)).first_or_404()
#    teachers = CoachingTeachers.query.filter_by(user_id2=coachingUserId.user_id).all()
#    coachingSlideImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' + 'CoachingClassSliderfile*' + '*.jpg')
#    coachingAchievementImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' + 'CoachingClassAchievementfile*' + '*.jpg')
#    coachingResultsImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coachingUserId.user_id) + '_' + '*' + '_' + 'CoachingClassResultsfile*' + '*.jpg')
#    if request.form.get('submit') == 'submit':
#        coaching_id = current_user.id
#        filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
#        for file in filefield:
#            f = request.files[file]
#            if f.filename:
#                f.filename = str(coachingUserId.user_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
#                filename = secure_filename(f.filename)
#                f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
#        Coaching = CoachingClass.query.get(key)
#        Coaching.coachingname = form.coachingname.data
#        Coaching.coachingcontact = form.coachingcontact.data
#        Coaching.coachingemail = form.coachingemail.data
#        Coaching.coachingabout = form.coachingabout.data
#        Coaching.coachingcategory = form.coachingcategory.data 
#        Coaching.coachinglocation = form.coachinglocation.data 
#        db.session.commit()
#    elif request.method == 'GET':
#        Coaching = CoachingClass.query.get(key)
#        form.coachingname.data = Coaching.coachingname
#        form.coachingcontact.data = Coaching.coachingcontact
#        form.coachingemail.data = Coaching.coachingemail
#        form.coachingabout.data = Coaching.coachingabout
#        form.coachingcategory.data = Coaching.coachingcategory
#        form.coachinglocation.data = Coaching.coachinglocation
#    return render_template('edit_coaching.html', title='Edit Coaching',
#                           form=form, coachingSlideImg_list=coachingSlideImg_list, coachingAchievementImg_list=coachingAchievementImg_list, coachingResultsImg_list=coachingResultsImg_list,teachers=teachers)

@app.route('/uploadHomeImages', methods = ['GET', 'POST'])
def uploadHomeImages():
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return redirect(url_for('home'))
   return render_template('uploadHomeImages.html')
	
@app.route('/manageHomeImages')
def manageHomeImages():
    #homeImg_list = os.listdir(app.config['UPLOAD_FOLDER'])
    homeImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/home")), '*.jpg')
    return render_template('manageHomeImages.html', homeImg_list=homeImg_list)		

@app.route('/deleteHomeImages/<filename>')
def deleteHomeImages(filename):
    file_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.remove(file_name)
    return redirect(url_for('manageHomeImages'))

@app.route('/uploadCoachingImages', methods = ['GET', 'POST'])
def uploadCoachingImages():
   if request.method == 'POST':
      coaching_id = current_user.coachingclass.all()[0].coachingid
      filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
      for file in filefield:
          f = request.files[file]
          if f.filename:
              f.filename = str(coaching_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
              filename = secure_filename(f.filename)
              f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
      return redirect(url_for('home'))
   return render_template('uploadCoachingImages.html')

@app.route('/deleteCoachingImages/<filename>', methods = ['GET', 'POST'])
def deleteCoachingImages(filename):
    file_name = os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename)
    os.remove(file_name)
    return redirect(url_for('adminupdatecoaching'))

@app.route('/deleteCoachingTeachers/<id>', methods = ['GET', 'POST'])
def deleteCoachingTeachers(id):
    teacherid=CoachingTeachers.query.get(id)
    db.session.delete(teacherid)
    db.session.commit()
    return redirect(url_for('adminupdatecoaching'))

@app.route('/contactMail', methods=['GET', 'POST'])
def contactMail():
    form = ContactMailForm()
    msg = Message("Customer Enquiry!!!",
      sender="studentsplateform@gmail.com",
      recipients=["studentsplateform@gmail.com"])
    msg.body = "A customer has enquired about Stuplate\n Please find the details below : \n Name : " + form.name.data + "\nEmail :" + form.email.data + "\nComments :" + form.comments.data + "\n\nThanks and Regards,\nStuplate Team"           
    mail.send(msg)
    flash('Thanks for enquiry. We will get back to you soon.')
    return redirect(url_for('home'))

@app.route("/studentregistration", methods=['GET', 'POST'])
def studentregistration():
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        regStudent = StudentDetails(studentname=form.studentname.data, studentcontact=form.studentcontact.data, studentgender=form.studentgender.data, studentaddress=form.studentaddress.data, studentfathersname=form.studentfathersname.data, studentqualification=form.studentqualification.data, studentlink=current_user)
        db.session.add(regStudent)
        db.session.commit()
        flash('Registration Complete!')
        return redirect(url_for('home'))
    return render_template('studentregistration.html', title='Register Student', form=form )

@app.route("/studentcoachingrelation", methods=['GET', 'POST'])
def studentcoachingrelation():
    form = StudentCoachingRelationForm()
    if form.validate_on_submit():
        StudentCoachingRel = StudentCoachingRelation(student_id=form.student_id.data, coaching_id=current_user.id, coachingTagIsActive='YES', CoachingBatch=form.CoachingBatch.data, CoachingSubject=form.CoachingSubject.data, CoachingPaidAmount=form.CoachingPaidAmount.data)
        db.session.add(StudentCoachingRel)
        db.session.commit()
        flash('Student has been tagged!')
        return redirect(url_for('home'))
    return render_template('studentcoachingrelation.html', title='Tag Student', form=form )

@app.route("/studentcoachinglist", methods=['GET', 'POST'])
def studentcoachinglist():
    #studentcoachinglists = StudentCoachingRelation.query.all()
    studentcoachinglists = StudentCoachingRelation.query.filter_by(coaching_id=str(current_user.id))
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id))
    StudentDet = StudentDetails.query.all()
    return render_template('studentcoachinglists.html', studentcoachinglists=studentcoachinglists, StudentDet=StudentDet, coachingbatches=coachingbatches)

@app.route("/studentcoachinguntaglist", methods=['GET', 'POST'])
def studentcoachinguntaglist():
    studentcoachinglists = StudentCoachingRelation.query.filter_by(coaching_id=str(current_user.id))
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id))
    StudentDet = StudentDetails.query.all()
    return render_template('studentcoachinguntaglist.html', studentcoachinglists=studentcoachinglists, StudentDet=StudentDet, coachingbatches=coachingbatches)

@app.route("/studentcoachinguntag/<key>", methods=['GET', 'POST'])
def studentcoachinguntag(key):
    StudentCoachingRel = StudentCoachingRelation.query.filter_by(id=key).first()
    StudentCoachingRel.coachingTagIsActive = 'NO'
    db.session.commit()
    return redirect(url_for('studentcoachinguntaglist'))

@app.route("/coachingfeesreciptlist", methods=['GET', 'POST'])
def coachingfeesreciptlist():
    studentcoachinglists = StudentCoachingRelation.query.filter_by(coaching_id=str(current_user.id),coachingTagIsActive='YES')
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id))
    StudentDet = StudentDetails.query.all()
    return render_template('coachingfeesreciptlist.html', studentcoachinglists=studentcoachinglists, StudentDet=StudentDet, coachingbatches=coachingbatches)

@app.route("/coachingfeesrecipt/<key>", methods=['GET', 'POST'])
def coachingfeesrecipt(key):
    StudentDet = StudentDetails.query.all()
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='YES')
    StudentCoachingRel = StudentCoachingRelation.query.filter_by(id=key).first()
    html = render_template('feeReceipt.html', StudentDet=StudentDet , StudentCoachingRel=StudentCoachingRel, coachingbatches=coachingbatches)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition '] = 'inline; filename=FeeReceipt.pdf'
    return response

@app.route("/coachingbatches", methods=['GET', 'POST'])
def coachingbatches():
    form = CoachingBatchesForm()
    if form.validate_on_submit():
        batchCoaching = CoachingBatches(batchname=form.batchname.data, batchdescription=form.batchdescription.data, batchstartdate=form.batchstartdate.data, batchenddate=form.batchenddate.data, batchfees=form.batchfees.data,batchIsActive='YES', batchlink=current_user)
        db.session.add(batchCoaching)
        db.session.commit()
        flash('New batch has been added!')
        return redirect(url_for('home'))
    return render_template('coachingbatch.html', title='Add Batch', form=form )
    
@app.route("/coachingbatchlist", methods=['GET', 'POST'])
def coachingbatchlist():
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='YES')
    CountStudDic = dict(StudentCoachingRelation.query.with_entities(StudentCoachingRelation.CoachingBatch,func.count(StudentCoachingRelation.CoachingBatch)).group_by(StudentCoachingRelation.CoachingBatch).filter_by(coaching_id=str(current_user.id)).all())
    return render_template('coachingbatchlist.html', coachingbatches=coachingbatches, CountStudDic=CountStudDic)

@app.route("/coachingbatchstudentlist/<key>", methods=['GET', 'POST'])
def coachingbatchstudentlist(key):
    StudentDet = StudentDetails.query.all()
    coachingBatchStudlist = StudentCoachingRelation.query.filter_by(coaching_id=str(current_user.id),CoachingBatch=key).all()
    return render_template('coachingbatchstudentlist.html', StudentDet=StudentDet, coachingBatchStudlist=coachingBatchStudlist)

@app.route("/studentdetails/<key>", methods=['GET', 'POST'])
def studentdetails(key):
    StudentDet = StudentDetails.query.all()
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id))
    StudentCoachingRel = StudentCoachingRelation.query.filter_by(id=key).first()
    html = render_template('feeReceipt.html', StudentDet=StudentDet , StudentCoachingRel=StudentCoachingRel, coachingbatches=coachingbatches)
    #html = render_template('studentdetails.html', StudentDet=StudentDet , StudentCoachingRel=StudentCoachingRel, coachingbatches=coachingbatches)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition '] = 'inline; filename=StudentDetail.pdf'
    return response

@app.route("/coachingdetailedinformation/<key>", methods=['GET', 'POST'])
def coachingdetailedinformation(key):
    stud = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id).distinct().filter_by(coaching_id=str(key)).count()
    studTagYES = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id.distinct()).filter_by(coaching_id=str(key),coachingTagIsActive='YES').count()
    studTagNO = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id.distinct()).filter_by(coaching_id=str(key),coachingTagIsActive='NO').count()
    CountCurrBatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='YES').count()
    CountInActiveBatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='NO').count()
    return render_template('coachingdetailedinformation.html', stud=stud, studTagYES=studTagYES, studTagNO=studTagNO, CountCurrBatches=CountCurrBatches,CountInActiveBatches=CountInActiveBatches)

@app.route("/totalcoachingstudentlist/<key>", methods=['GET', 'POST'])
def totalcoachingstudentlist(key):
    stud = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id).distinct().filter_by(coaching_id=str(key)).all()
    StudentDet = StudentDetails.query.all()
    return render_template('totalcoachingstudentlist.html', stud=stud, StudentDet=StudentDet)

@app.route("/coachingstudentlisttagyes/<key>", methods=['GET', 'POST'])
def totalcoachingstudentlisttagyes(key):
    studTagYES = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id.distinct()).filter_by(coaching_id=str(key),coachingTagIsActive='YES').all()
    StudentDet = StudentDetails.query.all()
    return render_template('totalcoachingstudentlisttagyes.html', studTagYES=studTagYES, StudentDet=StudentDet)

@app.route("/totalcoachingstudentlisttagno/<key>", methods=['GET', 'POST'])
def totalcoachingstudentlisttagno(key):
    studTagNO = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id.distinct()).filter_by(coaching_id=str(key),coachingTagIsActive='NO').all()
    StudentDet = StudentDetails.query.all()
    return render_template('totalcoachingstudentlisttagno.html', studTagNO=studTagNO, StudentDet=StudentDet)

@app.route("/coachingbatchinactivelist", methods=['GET', 'POST'])
def coachingbatchinactivelist():
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='YES').all()
    return render_template('coachingbatchinactivelist.html', coachingbatches=coachingbatches)

@app.route("/coachingbatchinactive/<key>", methods=['GET', 'POST'])
def coachingbatchinactive(key):
    coachingbatches = CoachingBatches.query.filter_by(id=key).first()
    coachingbatches.batchIsActive = 'NO'
    studentcoachinglists = StudentCoachingRelation.query.filter_by(CoachingBatch=key).all()
    for SCL in studentcoachinglists:
        SCL.coachingTagIsActive='NO'
    db.session.commit()
    return redirect(url_for('coachingbatchlist'))

@app.route("/coachinginactivebatchlist", methods=['GET', 'POST'])
def coachinginactivebatchlist():
    coachinginactivebatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='NO').all()
    CountStudDic = dict(StudentCoachingRelation.query.with_entities(StudentCoachingRelation.CoachingBatch,func.count(StudentCoachingRelation.CoachingBatch)).group_by(StudentCoachingRelation.CoachingBatch).filter_by(coaching_id=str(current_user.id)).all())
    return render_template('coachinginactivebatchlist.html', coachinginactivebatches=coachinginactivebatches,CountStudDic=CountStudDic)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Stuplate] Reset Your Password',
               sender='studentsplateform@gmail.com',
               recipients=[user.email],
               text_body=render_template('reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('reset_password.html',
                                         user=user, token=token))

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password_form.html', form=form)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

@app.route('/adminupdatecoaching', methods=['GET', 'POST'])
def adminupdatecoaching():
    page = request.args.get('page', 1, type=int)
    adminupdatecoachinglist = CoachingClass.query.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('adminupdatecoachinglist', page=adminupdatecoachinglist.next_num) \
        if adminupdatecoachinglist.has_next else None
    prev_url = url_for('adminupdatecoachinglist', page=adminupdatecoachinglist.prev_num) \
        if adminupdatecoachinglist.has_prev else None
    return render_template('adminupdatecoachinglist.html', adminupdatecoachinglist=adminupdatecoachinglist.items, next_url=next_url, prev_url=prev_url)

@app.route("/admindetailedinformation", methods=['GET', 'POST'])
def admindetailedinformation():
    stud = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id).distinct().filter_by(coaching_id=str(key)).count()
    studTagYES = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id.distinct()).filter_by(coaching_id=str(key),coachingTagIsActive='YES').count()
    studTagNO = StudentCoachingRelation.query.with_entities(StudentCoachingRelation.student_id.distinct()).filter_by(coaching_id=str(key),coachingTagIsActive='NO').count()
    CountCurrBatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='YES').count()
    CountInActiveBatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id),batchIsActive='NO').count()
    return render_template('admindetailedinformation.html', stud=stud, studTagYES=studTagYES, studTagNO=studTagNO, CountCurrBatches=CountCurrBatches,CountInActiveBatches=CountInActiveBatches)

@app.route('/studentdetailedinformation/<key>')
def studentdetailedinformation(key):
    studentdetail = StudentDetails.query.filter_by(user_idS=str(key)).first_or_404()
    if not studentdetail:
        abort(404)
    return render_template('studentdetailedinformation.html', studentdetail=studentdetail)

@app.route("/coachingteachersedit", methods=['GET', 'POST'])
def coachingteachersedit():
    form = CoachingTeachersEditForm()
    if request.form.get('submit_teachers') == 'Submit':
        filename1 = secure_filename(form.teachers_image.data.filename)
        form.teachers_image.data.save(app.config['UPLOAD_TEACHERS_FOLDER'] + filename1)
        url = images.url(filename1)
        coachingteachers = CoachingTeachers(teachersname=form.teachersname.data, teachersqualification=form.teachersqualification.data, teacherssubject=form.teacherssubject.data, teachersexperience=form.teachersexperience.data, image_filename=filename1, image_url=url, teacher=current_user)
        db.session.add(coachingteachers)
        db.session.commit()
        return redirect(url_for('productList'))
    return render_template('coachingteachersedit.html', title='Add Teachers', form=form )

@app.route("/updatecoachingfees/<key>", methods=['GET', 'POST'])
def updatecoachingfees(key):
    form = UpdateCoachingFeesForm()
    if form.validate_on_submit():
        StudCoaRel = StudentCoachingRelation.query.get(key)
        StudCoaRel.student_id = form.student_id.data
        StudCoaRel.CoachingBatch = form.CoachingBatch.data
        StudCoaRel.CoachingSubject = form.CoachingSubject.data
        StudCoaRel.CoachingPaidAmount = form.CoachingPaidAmount.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('coachingfeesreciptlist'))
    elif request.method == 'GET':
        StudCoaRel = StudentCoachingRelation.query.get(key)
        form.student_id.data = StudCoaRel.student_id
        form.CoachingBatch.data = StudCoaRel.student_id
        form.CoachingSubject.data = StudCoaRel.CoachingSubject
        form.CoachingPaidAmount.data = StudCoaRel.CoachingPaidAmount
    return render_template('updatecoachingfees.html', title='Update Total Fees', form=form)

@app.route('/testss', methods=["GET","POST"])
@login_required
def testss():
    tim = (request.args.get("testp"))
    print(tim)  #this gives excepted output.
    if request.method == 'POST':
        return redirect(url_for('testss'), time1=tim)
    if request.method == 'GET' and tim is not None:
        print('ixxxxxxxtim')  #this gives excepted output.
        return 'iiiiiiiiiiii'
    return render_template("test.html", time1=tim)

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
    usertype = SelectField('User Type', choices = [('Admin', 'Admin'), ('Coaching', 'Coaching'), ('Student', 'Student')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class UpdateNewsForm(FlaskForm):
    news = StringField('News', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CoachingRegistrationForm(FlaskForm):
    coachingname = StringField('coachingname')
    coachingcontact = StringField('Contact')
    coachingemail = StringField('Email')
    coachingabout = TextAreaField('About')
    coachingcategory = SelectField('Category', choices = [('Academic', 'Academic'), ('Entrance', 'Entrance'), ('Competition', 'Competition'), ('ComputerClasses', 'Computer Classes'), ('SpokenEnglishClasses', 'Spoken English Classes'), ('Others', 'Others')])
    coachinglocation = SelectField('Location', choices = [('Patna', 'Patna'), ('Pune', 'Pune'), ('Mumbai', 'Mumbai'), ('Bokaro', 'Bokaro')])
    teachersname = StringField('Teachers Name')
    teachersqualification = StringField('Teachers Qualification')
    teacherssubject = StringField('Teachers Subject')
    teachersexperience = StringField('Teachers Experience')
    teachers_image = FileField('Teachers Image')
    submit_teachers = SubmitField('Submit')

class StudentRegistrationForm(FlaskForm):
    studentname = StringField('Full Name')
    studentcontact = StringField('Contact')
    studentgender = SelectField('Gender', choices = [('Male', 'Male'), ('Female', 'Female')])
    studentaddress = StringField('Full Address')
    submit = SubmitField('Submit')

class StudentCoachingRelationForm(FlaskForm):
    student_id = StringField('Student ID')
    CoachingBatch = StringField('Batch ID')
    CoachingSubject = StringField('Description/Subject')
    CoachingPaidAmount = StringField('Paid Amount')
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
    coachinglocation = SelectField('Location', choices = [('Patna', 'Patna'), ('Pune', 'Pune'), ('Mumbai', 'Mumbai'), ('Bokaro', 'Bokaro')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class ContactMailForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=0, max=140)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    comment = StringField('Comment', validators=[DataRequired()])
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
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(coachingUserId.user_id))
    teachers = CoachingTeachers.query.filter_by(user_id2=coachingUserId.user_id).all()
    CoachingClassSliderimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(current_user.id) + '_' + '*' + '_' +'CoachingClassSliderfile*' + '_' + '*.jpg')
    CoachingClassAchievementimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(current_user.id) + '_' + '*' + '_' +'CoachingClassAchievementfile' + '_' + '*.jpg')
    CoachingClassResultsimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(current_user.id) + '_' + '*' + '_' +'CoachingClassResultsfile' + '_' + '*.jpg')
    if not item:
        abort(404)
    return render_template('item.html', item=item, CoachingClassSliderimages=CoachingClassSliderimages, CoachingClassAchievementimages=CoachingClassAchievementimages, CoachingClassResultsimages=CoachingClassResultsimages, teachers=teachers, coachingbatches=coachingbatches)

@app.route('/productList')
def productList():
    productsList = CoachingClass.query.all()
    return render_template('productList.html', productList=productsList)

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #if form.usertype.data == 'Coaching':
        user = User(username=form.email.data, email=form.email.data, usertype=form.usertype.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
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
    coachingSlideImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassSliderfile*' + '*.jpg')
    coachingAchievementImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassAchievementfile*' + '*.jpg')
    coachingResultsImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassResultsfile*' + '*.jpg')
    if request.form.get('submit') == 'submit_images':
        coaching_id = current_user.id
        filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
        for file in filefield:
            f = request.files[file]
            if f.filename:
                f.filename = str(coaching_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
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

def edit_coaching(key):
    form = EditCoachingForm()
    mycoaching = CoachingClass.query.get(key)
    coaching_id = current_user.id
    coachingUserId = CoachingClass.query.filter_by(coachingid=str(key)).first_or_404()
    teachers = CoachingTeachers.query.filter_by(user_id2=coachingUserId.user_id).all()
    coachingSlideImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassSliderfile*' + '*.jpg')
    coachingAchievementImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassAchievementfile*' + '*.jpg')
    coachingResultsImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassResultsfile*' + '*.jpg')
    if request.form.get('submit') == 'submit':
        coaching_id = current_user.id
        filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
        for file in filefield:
            f = request.files[file]
            if f.filename:
                f.filename = str(coaching_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
        Coaching = CoachingClass.query.get(key)
        Coaching.coachingname = form.coachingname.data
        Coaching.coachingcontact = form.coachingcontact.data
        Coaching.coachingemail = form.coachingemail.data
        Coaching.coachingabout = form.coachingabout.data
        Coaching.coachingcategory = form.coachingcategory.data 
        Coaching.coachinglocation = form.coachinglocation.data 
        db.session.commit()
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
    coaching_id = current_user.coachingclass.all()[0].coachingid
    file_name = os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename)
    os.remove(file_name)
    return redirect(url_for('edit_coaching' , key=coaching_id))

@app.route('/deleteCoachingTeachers/<id>', methods = ['GET', 'POST'])
def deleteCoachingTeachers(id):
    coaching_id = current_user.coachingclass.all()[0].coachingid
    teacherid=CoachingTeachers.query.get(id)
    db.session.delete(teacherid)
    db.session.commit()
    return redirect(url_for('edit_coaching' , key=coaching_id))

@app.route('/contactMail', methods=['GET', 'POST'])
def contactMail():
    form = ContactMailForm()
    msg = Message("Customer Enquiry!!!",
      sender="shivendra.ds48@gmail.com",
      recipients=["shivendrakushwaha022@gmail.com"])
    msg.body = "A customer has enquired about Stuplate\n Please find the details below : \n Name : " + form.name.data + "\nEmail :" + form.email.data + "\nComments :" + form.comment.data + "\n\nThanks and Regards,\nStuplate Team"           
    mail.send(msg)
    flash('Thanks for enquiry. We will get back to you soon.')
    return redirect(url_for('home'))

@app.route("/studentregistration", methods=['GET', 'POST'])
def studentregistration():
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        regStudent = StudentDetails(studentname=form.studentname.data, studentcontact=form.studentcontact.data, studentgender=form.studentgender.data, studentaddress=form.studentaddress.data, studentlink=current_user)
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
    studentcoachinglists = StudentCoachingRelation.query.filter_by(coaching_id=str(current_user.id))
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id))
    StudentDet = StudentDetails.query.all()
    return render_template('coachingfeesreciptlist.html', studentcoachinglists=studentcoachinglists, StudentDet=StudentDet, coachingbatches=coachingbatches)

@app.route("/coachingfeesrecipt/<key>", methods=['GET', 'POST'])
def coachingfeesrecipt(key):
    StudentDet = StudentDetails.query.all()
    StudentCoachingRel = StudentCoachingRelation.query.filter_by(id=key).first()
    html = render_template('feeReceipt.html', StudentDet=StudentDet , StudentCoachingRel=StudentCoachingRel)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition '] = 'inline; filename=FeeReceipt.pdf'
    return response

@app.route("/coachingbatches", methods=['GET', 'POST'])
def coachingbatches():
    form = CoachingBatchesForm()
    if form.validate_on_submit():
        batchCoaching = CoachingBatches(batchname=form.batchname.data, batchdescription=form.batchdescription.data, batchstartdate=form.batchstartdate.data, batchenddate=form.batchenddate.data, batchfees=form.batchfees.data, batchlink=current_user)
        db.session.add(batchCoaching)
        db.session.commit()
        flash('New batch has been added!')
        return redirect(url_for('home'))
    return render_template('coachingbatch.html', title='Add Batch', form=form )
    
@app.route("/coachingbatchlist", methods=['GET', 'POST'])
def coachingbatchlist():
    coachingbatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id))
    CountStudDic = dict(StudentCoachingRelation.query.with_entities(StudentCoachingRelation.CoachingBatch,func.count(StudentCoachingRelation.CoachingBatch)).group_by(StudentCoachingRelation.CoachingBatch).filter_by(coaching_id=str(current_user.id)).all())
    return render_template('coachingbatchlist.html', coachingbatches=coachingbatches, CountStudDic=CountStudDic)

@app.route("/coachingbatchstudentlist/<key>", methods=['GET', 'POST'])
def coachingbatchstudentlist(key):
    StudentDet = StudentDetails.query.all()
    coachingBatchStudlist = StudentCoachingRelation.query.filter_by(coaching_id=str(current_user.id),CoachingBatch=key).all()
    return render_template('coachingbatchstudentlist.html', StudentDet=StudentDet, coachingBatchStudlist=coachingBatchStudlist)

@app.route("/studentdetails/<key>", methods=['GET', 'POST'])
def studentdetails(key):
    StudentDet = StudentDetails.query.filter_by(studentid=key).all()
    html = render_template('studentdetails.html', StudentDet=StudentDet)
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
    CountCurrBatches = CoachingBatches.query.filter_by(user_idB=str(current_user.id)).count()
    return render_template('coachingdetailedinformation.html', stud=stud, studTagYES=studTagYES, studTagNO=studTagNO, CountCurrBatches=CountCurrBatches)

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

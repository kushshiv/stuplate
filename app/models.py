from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    usertype = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    coachingclass = db.relationship('CoachingClass', backref='author', lazy='dynamic')
    coachingteachers = db.relationship('CoachingTeachers' , backref='teacher', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id1 = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Newsticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news = db.Column(db.String(140))
    
    def __repr__(self):
        return '<NewsTicker {}>'.format(self.news)

class CoachingClass(db.Model):
    coachingid = db.Column(db.Integer, primary_key=True)
    coachingname = db.Column(db.String(140))
    coachingcontact = db.Column(db.Integer)
    coachingemail = db.Column(db.String(140))
    coachingpassword_hash = db.Column(db.String(128))
    coachingabout = db.Column(db.String(140))
    coachingcoursesoffered = db.Column(db.String(140))
    coachingteachers = db.Column(db.String(140))
    coachingachievement = db.Column(db.String(140))
    coachingresults = db.Column(db.String(140))
    coachingcategory = db.Column(db.String(140))
    coachingsubcategory = db.Column(db.String(140))
    coachinglocation = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return '<CoachingClass {}>'.format(self.coachingname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CoachingTeachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teachersname = db.Column(db.String(140))
    teachersqualification = db.Column(db.String(140))
    teacherssubject = db.Column(db.String(140))
    teachersexperience = db.Column(db.String(140))
    image_filename = db.Column(db.String, default=None, nullable=True)
    image_url = db.Column(db.String, default=None, nullable=True)
    user_id2 = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Teachers {}>'.format(self.teachersname)


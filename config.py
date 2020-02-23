import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FILE_FOLDER = os.getcwd() + '/app/static/'
    UPLOAD_FOLDER = os.getcwd() + '/app/static/img/home/'
    UPLOAD_COACHING_FOLDER = os.getcwd() + '/app/static/img/coaching_slide/'
    UPLOAD_TEACHERS_FOLDER = os.getcwd() + '/app/static/img/coaching_teachers/'
    UPLOADS_DEFAULT_DEST = os.getcwd() + '/app/static/img/coaching_teachers/'
    UPLOADS_DEFAULT_URL = os.getcwd() + '/app/static/img/coaching_teachers/'
    POSTS_PER_PAGE = 5
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_TLS = False
    MAIL_USE_SSL= True
    MAIL_USERNAME = 'studentsplateform@gmail.com'
    MAIL_PASSWORD = '7004099492'
    SECRET_KEY = 'sjkfjlsdjflasdfjkldjflksdfjksdjlfsd'

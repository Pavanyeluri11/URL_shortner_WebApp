from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import random
import string
import pyperclip as pc

#Creating the Application Server using flask
app = Flask(__name__)

#########################################
############DATABASE CONNECTIVITY########
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app , db)

@app.before_first_request
def create_tables():
    db.create_all()
###########################################
###########################################

class Urls(db.Model):
    __tablename__ = 'Urls'
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10))

    def __init__(self, long, short):
        self.long = long
        self.short = short
    
    def __repr__(self):
        return f"Short : {self.short} \n  long_url :{self.long}"

def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase + '0'+'1'+'2'+'3'+'4'+'5'+'6'+'7'+'8'+'9'
    while True:
        rand_letters = random.choices(letters, k=4)
        rand_letters = "".join(rand_letters)
        #making sure that same randoms letters is not given to two similar urls
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters




#############################################
#############################################

@app.route('/',methods=['POST','GET'])
def home():
    if request.method == 'POST':
        url_received = request.form.get('url')

        # check if url already exists in db
        found_url = Urls.query.filter_by(long=url_received).first()
        if found_url:
            # return short url if found
            short = 'http://127.0.0.1:5000/' + found_url.short
            pc.copy(short)
            return render_template('display_url.html',short_url=short)
        
        else:
            # create short url if not found
            short_url = shorten_url()
            new_url = Urls(url_received,short_url)
            short = 'http://127.0.0.1:5000/' + short_url
            pc.copy(short)
            db.session.add(new_url)
            db.session.commit()
            return render_template('display_url.html',short_url=short) 
            
    else:
         return render_template('homepage.html')

@app.route('/history')
def history():
    history = Urls.query.all()
    return render_template("history.html", history=history)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>Url doesnt exist</h1>'
###############################################
###############################################

if __name__ == '__main__':
    app.run(debug=True)
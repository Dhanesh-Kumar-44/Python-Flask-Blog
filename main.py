from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import math
from werkzeug.utils import secure_filename
from flask_mail import Mail

with open("config.json", "r") as c:
    params = json.load(c)["params"]

local_server = True
# db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['user_email'],
    MAIL_PASSWORD = params['password']
)
mail = Mail(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/codingthunder'
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
# db.init_app(app)
db = SQLAlchemy(app)


class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20),nullable=True)


class Posts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(12), nullable=False)
    tagline = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(20),nullable=True)
    img_file = db.Column(db.String(20),nullable=True)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    print("len(posts)",len(posts))
    last = int(math.floor(len(posts)/params['no_of_posts']))
    page = request.args.get("page")
    print("page===",page)
    if not str(page).isdigit():
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    #pagination logic
    #first
    print("last===",last)
    print("page===",page)
    if page == 1:
        prev = "#"
        next = "/?page"+str(page+1)
    elif page == last:
        prev = "/?page"+str(page-1)
        next = "#"
    else:
        prev = "/?page" + str(page - 1)
        next = "/?page" + str(page + 1)
    print("next==",next)
    print("prev==",prev)

    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)
    # return "<p>Hello, World!</p>"

@app.route("/about")
def about():
    # name="Dhanesh"
    return render_template('about.html',params=params)

@app.route("/edit/<string:sno>", methods=['GET','POST'])
def edit(sno):
    print("check added data==",sno,request.method)
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno == '0':
                print("check added data==")
                post = Posts(title=title, slug=slug, content=content, tagline=tagline, img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
                return redirect('/edit/' + sno)
                # return render_template('edit.html',params=params,post=post)
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.tagline = tagline
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
                # return render_template('dashboard.html', params=params)
        post = Posts.query.filter_by(sno=sno).first()
        if not post:
            post = {}
            post['sno'] = '0'
        print("post===",post)
        return render_template('edit.html',params=params,post=post)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():

    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)
    if request.method == 'POST':
    #     redirect to admin panel
        username = request.form.get('uname')
        userpass = request.form.get('password')
        print("request_get",request.form)
        print("request_get",userpass)
        print("request_get",username)
        print("request_get",userpass == params['admin_password'])
        print("request_get",username == params['admin_user'] )
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)

    return render_template('login.html',params=params)

@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
    print("post_slug==",post_slug)
    post = Posts.query.filter_by(slug=post_slug).first()
    print("post data",post)
    return render_template('post.html',params=params, post=post)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if request.method=='POST':
        # Add entry into database...
        '''
         sno, name, email, phone_num, msg, date
         '''
        name = request.form.get('name')
        email = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')

        # entry = Contacts(name=name, email=email, phone_num=phone, msg=message, date=datetime.now())
        # db.session.add(entry)
        # db.session.commit()
        #sending mail
        mail.send_message("New message from "+ name,
                          sender=email,
                          recipients=[params['user_email']],
                          body=message + "\n"+ phone)
    return render_template('contact.html',params=params)

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded Successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        # if request.method == 'POST':
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

app.run(debug=True)
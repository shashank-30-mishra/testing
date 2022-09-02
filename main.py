
import os,math
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
#from notify_run import Notify
#from flask_mail import Mail
import json
from datetime import date, datetime
import bcrypt


local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key='super-secret-key'
app.config['UPLOAD_FOLDER']=params['file_location']
app.config['ALLOWED_EXTENSIONS'] = params['file_format']
app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1000
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['mail_id'],
    MAIL_PASSWORD = params['psswd']
)

#mail = Mail(app)
#notify=Notify()

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    Sr_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class User(db.Model):
    srno = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(20), nullable=False)
    psswd = db.Column(db.String(20), nullable=False)
    creation_time = db.Column(db.String(12),nullable=True)

class Posts(db.Model):
    '''
    Sr. no., title, slug, content, date
    '''
    Sr_no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(50), nullable=False)
    tagline = db.Column(db.String(50), nullable=False)

@app.route("/",methods=['GET'])
def home():
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_post']))
    page=request.args.get('page')

    if(not str(page).isdigit()):
        page=1
    page=int(page)
    # return str(last)
    if(page>last):
        return redirect("/?page="+str(last))
    post=posts[(page-1)*int(params['no_post']):(page-1)*int(params['no_post'])+int(params['no_post'])]

    if(page==1):
        prev = "#"
        next = "/?page="+str(page+1)
    elif(page ==last):
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)



    return render_template('index.html', params=params,posts=post,prev=prev, next=next)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    posts=Posts.query.all()
    if('user' in session and session['user']==params['admin_name']):
        return render_template("dashboard.html", params=params,posts=posts)

    if(request.method=='POST'):
        username = request.form.get('user_name')
        userpsswd = request.form.get('user_psswd')
        if(username==params['admin_name'] and userpsswd==params['admin_psswd']):
            session['user']=username
            return render_template("dashboard.html", params=params,posts=posts)
        else:
            return render_template("login.html", params=params)

    else:
        return render_template("login.html", params=params)

@app.route("/user_login", methods=['GET','POST'])
def user_login():
    if(request.method=='POST'):
        user = User.query.filter_by(email=request.form.get('user_name')).first()
        userpsswd = request.form.get('user_psswd').encode("utf-8")
        # return user.email
        if user:
            if bcrypt.checkpw(userpsswd, user.psswd.encode("utf-8")):
                return redirect("/")
            else:
                return "Please ennter correct Password and login."
        else:
            return "Your account does not exist. Please create your account."


@app.route("/sign_up",methods=['GET','POST'])
def sign_up():
    if (request.method=='POST'):
        username = request.form.get('user_name')
        userpsswd1 = request.form.get('user_psswd1')
        userpsswd2 = request.form.get('user_psswd2')

        if User.query.filter_by(email=request.form.get('user_name')).first():
            return "You have already registered."


        if (userpsswd1!=userpsswd2 or len(userpsswd1)==0):
            return "Mismatch in both passwords. Please confirm the same password or No password entered. Please check."
        else:
            signup = User(email=username,psswd=bcrypt.hashpw(userpsswd1.encode("utf-8"), bcrypt.gensalt()),creation_time= datetime.now())
            db.session.add(signup)
            db.session.commit()
            return "Your account created successfully. Thanks for joining us"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")

@app.route("/delete/<string:Sr_no>" , methods=['GET', 'POST'])
def delete(Sr_no):
    if('user' in session and session['user']==params['admin_name']):
        post=Posts.query.filter_by(Sr_no=Sr_no).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/edit/<string:Sr_no>" , methods=['GET', 'POST'])
def edit(Sr_no):
    if('user' in session and session['user']==params['admin_name']):
        if request.method=='POST':
            box_title=request.form.get('title')
            tagline=request.form.get('tagline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img=request.form.get('img_file')
            date=datetime.now()

            if Sr_no=='0':
                post=Posts(title=box_title,tagline=tagline,slug=slug,content=content, img_file=img,date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post=Posts.query.filter_by(Sr_no=Sr_no).first()
                post.title=box_title
                post.tagline=tagline
                post.slug=slug
                post.content=content
                post.img_file=img
                post.date=date
                db.session.commit()
                return redirect("/edit/"+Sr_no)

        post = Posts.query.filter_by(Sr_no=Sr_no).first()
        return render_template('edit.html', params=params,post=post,Sr_no=Sr_no )
        
    return redirect("/dashboard")
    
@app.route("/uploader", methods=['GET', 'POST'])
def upload():
    if('user' in session and session['user']==params['admin_name']):
        if request.method=='POST':
            f=request.files['file1']
            # open(params['file_location']+"\\"+f.filename).close()
            f.save(os.path.join(app.config['UPLOAD_FOLDER'] , secure_filename(f.filename)))
            return "File Uploaded Successfully"
        
@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/post/<string:post_slug>" , methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()


    return render_template('post.html', params=params, post=post)


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New message from ' + name,
        # sender=email,
        # recipients = [params['mail_id']],
        # body = message + "\n" + phone
        #     )  
 #       notify.send('{} have sent a meassage.\n Mob. No. {}.\nmessage-: {} '.format(name,phone,message)) 
    return render_template('contact.html', params=params)


#app.run(debug=True)
if __name__ == '__main__':
  app.run(host='0.0.0.0',port=8080,debug=True)

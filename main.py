from flask import Flask, request, redirect, render_template, flash, session
# import cgi
# from app import app
# from models import Blog
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpass314@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'iuwue812812'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    posted_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, posted_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if posted_date is None:
            posted_date = datetime.utcnow()
        self.posted_date = posted_date
        

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    if request.method == 'GET' :
        return render_template('newpost.html')

    title = request.form['title']
    body = request.form['body']
    owner = User.query.filter_by(username=session['username']).first()

    title_error = ''
    body_error = ''

    if title == "":
        title_error = "Title required."
    if body == "":
        body_error = "Content required."

    if not title_error and not body_error:
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        page_id = new_post.id
        return redirect("/blog?id={0}".format(page_id))
    else:
        return render_template('newpost.html', 
        title = title, body = body, title_error = title_error, body_error = body_error)


def posted_blog():
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.posted_date = True
    db.session.add(blog)
    db.session.commit()
    return redirect('/newpost')

@app.route('/blog', methods=['POST', 'GET'])
def blog():    
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')

    posts = Blog.query.order_by(Blog.posted_date.desc())

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("posted-blog.html", title=post.title, body=post.body, user=post.owner_id, posted_date=post.posted_date, user_id=post.owner_id)
    if user_id:
        entries = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', entries=entries)

    return render_template('blog.html', posts=posts)

    

@app.route('/')
def index():   
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #TODO - validate user's data
        print("User in request " + username + " " + password)
        existing_user =  User.query.filter_by(username=username).first()
        username_error = ""
        password_error = ""
        verify_error = ""

        if username == "":
            username_error = "Enter Username."
        elif len(username) <= 3 or len(username) > 20:
            username_error = "Username must be between 3 and 20 characters long."
        elif " " in username:
            username_error = "Username can't contain any spaces."
        if password == "":
            password_error = "Please enter a password."
        elif len(password) <= 3:
            password_error = "Password must be greater than 3 characters long."
        elif " " in password:
            password_error = "Password can't contain any spaces."
        if password != verify or verify == "":
            verify_error = "Passwords don't match."
        if existing_user:
            username_error = "Username already exist."
        # If fields are good, continue to creating session with new username and password.
        if len(username) >= 3 and len(password) >= 3 and password == verify and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return render_template('newpost.html')
        else:
            return render_template('signup.html', 
            username=username, 
            username_error=username_error,
            password_error=password_error,
            verify_error=verify_error)

    return render_template('signup.html')

            
            

@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    password_error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        else:
            return render_template('login.html', password_error="User password incorrect, or user does not exist.")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()

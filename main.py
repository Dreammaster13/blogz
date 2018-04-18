from flask import Flask, request, redirect, render_template, flash
# import cgi
# from app import app
# from models import Blog
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'iuwue812812'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    posted = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.posted = False



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_title_error = ''
    blog_body_error = ''
    if request.method == 'POST':
        blog_title = request.form.get('blog-title')
        if len(blog_title) < 1:
            blog_title_error = ('Title is too short!')
        blog_body = request.form.get('blog-body')
        if len(blog_body) < 1:
            blog_body_error = ('Blog is too short! Drop something else!')
        if any([blog_body_error, blog_title_error]):
            return render_template('newpost.html', blog_title_error=blog_title_error,
             blog_body_error=blog_body_error, blog_body=blog_body, blog_title=blog_title)
        else:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            blog = Blog.query.get(new_blog_id)
            return render_template('/blog.html', blog=blog)

    return render_template('newpost.html', title="Add new Blog Post")

def posted_blog():
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.posted = True
    db.session.add(blog)
    db.session.commit()
    return redirect('/newpost')

@app.route('/blog', methods=['GET'])
def blog():    
    blog_id = int(request.args.get('id'))
    blog = Blog.query.get(blog_id)    
    return render_template('blog.html', blog=blog)
    

@app.route('/', methods=['GET','POST'])
def index():   
    posted_blogs = Blog.query.all()
    return render_template('index.html',posted_blogs=posted_blogs)

if __name__ == '__main__':
    app.run()

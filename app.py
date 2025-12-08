from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import bleach




load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'SECRET'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # type: ignore


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def sanitize_input(text):
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'code', 'pre', 'blockquote']
    allowed_attrs = {}
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs, strip=True)


#Database Models --------------------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')      
    

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)    






# Routes ---------------------------------------



@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in...', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", 'success')
    return redirect(url_for('index'))



@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_admin:
        flash('Only admins can create posts', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = sanitize_input(request.form['title'])
        content = sanitize_input(request.form['content'])

        new_post = Post(title=title, content=content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('index'))
    

    return render_template('create_post.html')




@app.route('/post/<int:id>')
def view_post(id):
    post = Post.query.get_or_404(id)
    return render_template('view_post.html', post=post)



@app.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)

    if not current_user.is_admin:
        flash('Only admins can edit posts', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        post.title  = sanitize_input(request.form['title'])
        post.content = sanitize_input(request.form['content'])
        post.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Post updated successfully!', 'success')
        return redirect(url_for('view_post', id=post.id))
    
    return render_template('edit_post.html', post=post) 



@app.route('/post/<int:id>/delete')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)

    if not current_user.is_admin:
        flash('Only admins can delete posts', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(post)
    db.session.commit()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = sanitize_input(request.form['content'])

    new_comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()

    flash('Comment added', 'success')
    return redirect(url_for('view_post', id=post_id))




@app.route('/comment/<int:id>/delete')
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id

    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You can only delete your own comments', 'error')
        return redirect(url_for('view_post', id=post_id))
    
    db.session.delete(comment)
    db.session.commit()

    flash('Comment deleted', 'success')
    return redirect(url_for('view_post', id=post_id))


@app.route("/admin/users")
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route("/admin/user/<int:id>/delete")
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.username} deleted successfully!', 'success')
    return redirect(url_for('admin_users'))


with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)

    

    



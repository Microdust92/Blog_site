import pytest
from flask_testing import TestCase
from app import app, db, User, Post, Comment



# Test Cmd:   python -m pytest tests/test_app.py -v


class BaseTestCase(TestCase):
    """Base test case with database setup"""
    
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        return app
    
    def setUp(self):
        db.create_all()
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()


# ===== User Tests =====

class UserTestCase(BaseTestCase):
    """Test user registration and authentication"""
    
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }, follow_redirects=True)
        
        self.assert200(response)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')
    
    def test_duplicate_username_rejected(self):
        """Test duplicate username is rejected"""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'pass123'
        }, follow_redirects=True)
        
        self.assert200(response)
        self.assertIn(b'Username already exists', response.data)
    
    def test_user_login(self):
        """Test user can login"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assert200(response)
        self.assertIn(b'Logged in successfully', response.data)
    
    def test_invalid_login(self):
        """Test invalid credentials rejected"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assert200(response)
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_password_hashing(self):
        """Test passwords are hashed"""
        self.assertNotEqual(self.user.password_hash, 'password123')
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.check_password('wrongpass'))


# ===== Post Tests =====

class PostTestCase(BaseTestCase):
    """Test post CRUD operations"""
    
    def login(self):
        """Helper to login test user"""
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def test_create_post_requires_login(self):
        """Test creating post requires authentication"""
        response = self.client.get('/post/new')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_post(self):
        """Test authenticated user can create post"""
        self.login()
        response = self.client.post('/post/new', data={
            'title': 'Test Post',
            'content': 'This is a test post content.'
        }, follow_redirects=True)
        
        self.assert200(response)
        post = Post.query.filter_by(title='Test Post').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.content, 'This is a test post content.')
        self.assertEqual(post.user_id, self.user.id)
    
    def test_view_post(self):
        """Test viewing a post"""
        post = Post(title='View Test', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        response = self.client.get(f'/post/{post.id}')
        self.assert200(response)
        self.assertIn(b'View Test', response.data)
    
    def test_edit_own_post(self):
        """Test user can edit their own post"""
        self.login()
        post = Post(title='Original', content='Original content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        response = self.client.post(f'/post/{post.id}/edit', data={
            'title': 'Updated Title',
            'content': 'Updated content'
        }, follow_redirects=True)
        
        self.assert200(response)
        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.content, 'Updated content')
    
    def test_delete_own_post(self):
        """Test user can delete their own post"""
        self.login()
        post = Post(title='Delete Me', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        
        response = self.client.get(f'/post/{post_id}/delete', follow_redirects=True)
        self.assert200(response)
        
        deleted_post = Post.query.get(post_id)
        self.assertIsNone(deleted_post)
    
    def test_cannot_edit_others_post(self):
        """Test user cannot edit another user's post"""
        # Create another user and their post
        other_user = User(username='other', email='other@example.com')
        other_user.set_password('pass123')
        db.session.add(other_user)
        db.session.commit()
        
        post = Post(title='Other Post', content='Content', user_id=other_user.id)
        db.session.add(post)
        db.session.commit()
        
        # Login as test user and try to edit
        self.login()
        response = self.client.post(f'/post/{post.id}/edit', data={
            'title': 'Hacked',
            'content': 'Hacked'
        }, follow_redirects=True)
        
        self.assert200(response)
        self.assertIn(b'You can only edit your own posts', response.data)


# ===== Comment Tests =====

class CommentTestCase(BaseTestCase):
    """Test comment operations"""
    
    def login(self):
        """Helper to login test user"""
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def test_add_comment_requires_login(self):
        """Test adding comment requires authentication"""
        post = Post(title='Test', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        response = self.client.post(f'/post/{post.id}/comment', data={
            'content': 'Test comment'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_add_comment(self):
        """Test authenticated user can add comment"""
        self.login()
        post = Post(title='Test', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        response = self.client.post(f'/post/{post.id}/comment', data={
            'content': 'Great post!'
        }, follow_redirects=True)
        
        self.assert200(response)
        comment = Comment.query.filter_by(content='Great post!').first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.post_id, post.id)
        self.assertEqual(comment.user_id, self.user.id)
    
    def test_delete_own_comment(self):
        """Test user can delete their own comment"""
        self.login()
        post = Post(title='Test', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        comment = Comment(content='Delete me', user_id=self.user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id
        
        response = self.client.get(f'/comment/{comment_id}/delete', follow_redirects=True)
        self.assert200(response)
        
        deleted_comment = Comment.query.get(comment_id)
        self.assertIsNone(deleted_comment)


# ===== Database Tests =====

class DatabaseTestCase(BaseTestCase):
    """Test database relationships and constraints"""
    
    def test_user_post_relationship(self):
        """Test one-to-many relationship between users and posts"""
        post1 = Post(title='Post 1', content='Content 1', user_id=self.user.id)
        post2 = Post(title='Post 2', content='Content 2', user_id=self.user.id)
        db.session.add_all([post1, post2])
        db.session.commit()
        
        self.assertEqual(len(self.user.posts), 2)
        self.assertEqual(post1.author.username, 'testuser')
    
    def test_post_comment_relationship(self):
        """Test one-to-many relationship between posts and comments"""
        post = Post(title='Test', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        comment1 = Comment(content='Comment 1', user_id=self.user.id, post_id=post.id)
        comment2 = Comment(content='Comment 2', user_id=self.user.id, post_id=post.id)
        db.session.add_all([comment1, comment2])
        db.session.commit()
        
        self.assertEqual(len(post.comments), 2)
    
    def test_cascade_delete_post(self):
        """Test deleting post also deletes its comments"""
        post = Post(title='Test', content='Content', user_id=self.user.id)
        db.session.add(post)
        db.session.commit()
        
        comment = Comment(content='Comment', user_id=self.user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id
        
        db.session.delete(post)
        db.session.commit()
        
        # Comment should be deleted due to cascade
        deleted_comment = Comment.query.get(comment_id)
        self.assertIsNone(deleted_comment)


if __name__ == '__main__':
    import unittest
    unittest.main()
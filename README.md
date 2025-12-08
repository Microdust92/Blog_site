# Walker Files Blog

A secure, feature-rich blog application built with Flask featuring admin controls, user management, and a dark cyberpunk aesthetic.

## Features

### Core Functionality
- **CRUD Operations**: Create, read, update, and delete blog posts and comments
- **User Authentication**: Secure registration and login system using Flask-Login
- **Role-Based Access Control**: Admin-only post creation and management
- **User Management**: Admin dashboard to view and manage all users
- **Comment System**: Authenticated users can comment on posts

### Security
- **Input Sanitization**: Bleach library prevents XSS attacks while allowing safe HTML
- **Password Hashing**: Werkzeug security for secure password storage
- **Admin-Only Controls**: Restricted post creation/editing to administrators
- **Session Management**: Flask-Login handles secure user sessions

### Design
- **Dark Cyberpunk Theme**: Custom CSS with cyan/purple gradient accents
- **Digital Rain Effect**: Matrix-style animated background
- **Responsive Design**: Mobile-friendly layout
- **Professional UI**: Modern card-based design with smooth animations

### Extra Features
- **Embedded Content**: Support for iframes and links in posts
- **User Statistics**: View post and comment counts per user
- **Relationship Management**: Cascade deletes maintain database integrity
- **Flash Messages**: User-friendly success/error notifications

## Technology Stack

- **Backend**: Flask 3.1.2
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login 0.6.3
- **Security**: Bleach 6.1.0 for input sanitization
- **Testing**: Flask-Testing 0.8.1 with 19 unit tests
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Blog_site
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   ```

6. **Initialize the database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

7. **Create admin user**
   Register a user through the web interface, then run:
   ```bash
   python make_admin.py
   ```
   This will promote the first user to admin status.

## Running the Application

1. **Start the Flask development server**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Testing

Run the test suite with:
```bash
python -m pytest tests/test_app.py -v
```

**Test Coverage:**
- 19 unit tests covering:
  - User registration and authentication (5 tests)
  - Admin-only post CRUD operations (7 tests)
  - Comment system with admin privileges (4 tests)
  - Database relationships and cascades (3 tests)

## Project Structure

```
Blog_site/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
├── .gitignore             # Git ignore rules
├── make_admin.py          # Admin promotion utility
├── static/
│   ├── css/
│   │   └── style.css      # Cyberpunk theme styles
│   └── js/
│       └── matrix-rain.js # Digital rain animation
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── view_post.html     # Single post view
│   ├── create_post.html   # Post creation form
│   ├── edit_post.html     # Post editing form
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── admin_users.html   # User management dashboard
│   ├── about.html         # About page
│   └── contact.html       # Contact page
├── tests/
│   └── test_app.py        # Unit tests
└── instance/
    └── blog.db            # SQLite database (created on first run)
```

## Database Schema

### User Model
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `is_admin`: Boolean admin flag
- `created_at`: Registration timestamp
- **Relationships**: One-to-many with Posts and Comments

### Post Model
- `id`: Primary key
- `title`: Post title
- `content`: Post content (sanitized HTML allowed)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `user_id`: Foreign key to User
- **Relationships**: One-to-many with Comments, Many-to-one with User

### Comment Model
- `id`: Primary key
- `content`: Comment content (sanitized)
- `created_at`: Creation timestamp
- `user_id`: Foreign key to User
- `post_id`: Foreign key to Post
- **Relationships**: Many-to-one with User and Post

## User Roles

### Regular Users
- Register and login
- View all posts and comments
- Add comments to posts
- Delete their own comments

### Administrators
- All regular user permissions
- Create, edit, and delete blog posts
- Delete any user's comments
- Access user management dashboard
- View user statistics
- Delete user accounts (except their own)

## Security Features

1. **Input Sanitization**: All user input is sanitized using Bleach
   - Allowed tags: `p, br, strong, em, u, h1-h4, ul, ol, li, code, pre, blockquote, a, iframe`
   - Allowed attributes: `href, title` on links; `src, width, height, frameborder` on iframes

2. **Password Security**: Passwords are hashed using Werkzeug's `pbkdf2:sha256`

3. **CSRF Protection**: Flask-Login provides session management

4. **SQL Injection Prevention**: SQLAlchemy ORM handles parameterized queries

## Extra Credit Features

✅ **Flask-Login**: Complete authentication system with login/logout and session management

✅ **Flask-Testing**: Comprehensive test suite with 19 passing tests

## Assignment Compliance

- ✅ Flask backend with routing
- ✅ Jinja2 templates for all pages
- ✅ Navigation routes to access all pages
- ✅ CRUD operations for posts, comments, and users
- ✅ Blog posts with create/view/edit functionality
- ✅ Comments with add/display/delete functionality
- ✅ Username displayed with posts and comments
- ✅ Login/Logout functionality
- ✅ Database tables with proper relationships
- ✅ Extra Module 1: Authentication (Flask-Login)
- ✅ Extra Module 2: Testing (Flask-Testing)

## Known Issues / Future Enhancements

### Potential Improvements
- Add user profile pages
- Implement profile picture uploads
- Add post categories/tags
- Include search functionality
- Add pagination for posts
- Implement email verification
- Add password reset functionality
- Create RSS feed for posts

## Credits

**Developer**: Will Walker
**Course**: CWEB 1116 - Web Development
**Institution**: Dunwoody College of Technology
**Semester**: Spring 2025

## License

This project is created for educational purposes as part of a college assignment.

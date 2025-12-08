from app import app, db, User

with app.app_context():
    # Get the first user (or change username to yours)
    user = User.query.first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"{user.username} is now an admin!")
    else:
        print("No users found")
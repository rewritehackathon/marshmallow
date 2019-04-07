from appFolder import db, login_mangager
from datetime import datetime
from flask_login import UserMixin

@login_mangager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique = True, nullable = False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    gpa = db.Column(db.String(4))
    school_year = db.Column(db.String(4))
    password = db.Column(db.String(40), nullable=False)
    last_login = db.Column(db.DateTime, nullable=False, default =  datetime.now())

    def __repr__(self):
        return f"User('{self.username}', '{self.password}')"

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(50),nullable=False)
    grade = db.Column(db.String(2), nullable = False)
    def __repr__(self):
        return f"User('{self.user_id}', '{self.subject}','{self.grade}')"

class Posts(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
     subject = db.Column(db.String(50), nullable=False)
     title = db.Column(db.String(50),nullable=False)
     content = db.Column(db.String(8000), nullable=False)

     def __repr__(self):
         return f"Posts('{self.id}', '{self.user_id}','{self.content}','{self.subject}','{self.title}')"

class Activites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(40), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    content = db.Column(db.String(8000), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.user_id}','{self.post_id}','{self.type}','{self.timestamp}','{self.content}')"






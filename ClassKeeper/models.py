from db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    picture = db.Column(db.String(120), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    picture = db.Column(db.String(120), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    grades = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String, nullable=True)
    address = db.Column(db.String(250), nullable=True)
    school_year = db.Column(db.String(9), nullable=True)
    notes = db.Column(db.Text, nullable=True) 

    def set_courses(self, courses):
        self.course = ",".join(courses)

    def get_courses(self):
        return self.course.split(",") if self.course else []

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False)  # Present, Absent, Late, etc.
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))

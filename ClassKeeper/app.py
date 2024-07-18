from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, User, Student, Attendance
from db import create_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = create_app()
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
            flash("You don't have permission to access this page", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(User=User)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        students = Student.query.all()
        return render_template('dashboard.html', user=user, students=students)
    else:
        return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_number = request.form['student_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        age = request.form['age']
        birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
        picture = request.files['picture']
        gender = request.form['gender']
        grades = request.form['grades']
        courses = request.form.getlist('course')
        address = request.form['address']
        school_year = request.form['school_year']

        # Convert the course list to a comma-separated string
        course_string = ",".join(courses)

        # Save the picture file if uploaded
        picture_filename = None
        if picture and picture.filename != '':
            picture_filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_filename))

        new_student = Student(
            student_number=student_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            age=age,
            birthday=birthday,
            picture=picture_filename,
            gender=gender,
            grades=grades,
            course=course_string,
            address=address,
            school_year=school_year
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Student added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_student.html')

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.student_number = request.form['student_number']
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.email = request.form['email']
        student.age = request.form['age']
        student.birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
        student.gender = request.form['gender']
        student.grades = request.form['grades']
        courses = request.form.getlist('course')
        student.address = request.form['address']
        student.school_year = request.form['school_year']

        # Convert the course list to a comma-separated string
        course_string = ",".join(courses)

        if 'picture' in request.files:
            file = request.files['picture']
            if file.filename != '':
                picture = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], picture))
                student.picture = picture

        student.course = course_string
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    students = Student.query.all()
    return render_template('admin_dashboard.html', users=users, students=students)

@app.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_admin = 'is_admin' in request.form
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        user.gender = request.form['gender']
        user.grades = request.form['grades']
        user.course = request.form['course']

        if 'picture' in request.files:
            file = request.files['picture']
            if file.filename != '':
                picture = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], picture))
                user.picture = picture

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:id>')
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    filter_by = request.args.get('filter')

    if filter_by == 'username':
        results = User.query.filter(User.username.contains(query)).all()
    elif filter_by == 'email':
        results = User.query.filter(User.email.contains(query)).all()
    elif filter_by == 'student_number':
        results = Student.query.filter(Student.student_number.contains(query)).all()
    elif filter_by == 'first_name':
        results = Student.query.filter(Student.first_name.contains(query)).all()
    elif filter_by == 'last_name':
        results = Student.query.filter(Student.last_name.contains(query)).all()
    elif filter_by == 'gender':
        results = Student.query.filter(Student.gender.contains(query)).all()
    elif filter_by == 'course':
        results = Student.query.filter(Student.course.contains(query)).all()
    elif filter_by == 'grades':
        results = Student.query.filter(Student.grades.contains(query)).all()
    else:
        results = []

    return render_template('search_results.html', results=results, query=query, filter_by=filter_by)

@app.route('/add_notes', methods=['GET', 'POST'])
def add_notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_id = request.form['student_id']
        notes = request.form['notes']
        
        student = Student.query.get_or_404(student_id)
        student.notes = notes
        db.session.commit()
        
        flash('Notes added successfully!', 'success')
        return redirect(url_for('add_notes'))

    students = Student.query.all()
    return render_template('add_notes.html', students=students)

@app.route('/view_notes')
def view_notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    students = Student.query.all()
    return render_template('view_notes.html', students=students)

@app.route('/delete_note/<int:id>', methods=['POST'])
def delete_note(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)
    student.notes = None
    db.session.commit()
    
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('view_notes'))

@app.route('/edit_note/<int:id>', methods=['POST'])
def edit_note(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)
    notes = request.form['notes']
    student.notes = notes
    db.session.commit()
    
    flash('Note updated successfully!', 'success')
    return redirect(url_for('view_notes'))

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_id = request.form['student_id']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        status = request.form['status']

        new_attendance = Attendance(student_id=student_id, date=date, status=status)
        db.session.add(new_attendance)
        db.session.commit()

        flash('Attendance recorded successfully!', 'success')
        return redirect(url_for('attendance'))

    students = Student.query.all()
    return render_template('attendance.html', students=students)

@app.route('/view_attendance')
def view_attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    attendances = Attendance.query.all()
    return render_template('view_attendance.html', attendances=attendances)

@app.route('/delete_attendance/<int:id>', methods=['POST'])
def delete_attendance(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    attendance = Attendance.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    
    flash('Attendance record deleted successfully!', 'success')
    return redirect(url_for('view_attendance'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

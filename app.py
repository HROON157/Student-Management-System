from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from sqlalchemy import or_
from flask_login import UserMixin, login_manager, login_user, logout_user, login_required, current_user,LoginManager
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# from models import db, Category, SubCategory, Query, Status

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/sms'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '11681168'  # Add a unique secret key
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    roles = db.relationship('Role', secondary='user_roles')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles')

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

class RolePermissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete='CASCADE'))

# Define your models based on the database schema
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    subcategories = db.relationship('SubCategory', back_populates='category')

class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    category = db.relationship('Category', back_populates='subcategories')
    queries = db.relationship('Query', back_populates='subcategory')

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    queries = db.relationship('Query', back_populates='status')

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone1 = db.Column(db.String(20), nullable=True)
    phone2 = db.Column(db.String(20), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    remarks = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.today)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    subcategory = db.relationship('SubCategory', back_populates='queries')
    status = db.relationship('Status', back_populates='queries')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subcourses = db.relationship('SubCourse', backref='course', lazy=True)
    teachers = db.relationship('TeacherCourse', backref='course', lazy=True)
    attendances = db.relationship('Attendance', backref='course', lazy=True)
    fees = db.relationship('Fee', backref='course', lazy=True)
    student_courses = db.relationship('StudentCourse', backref='course', lazy=True)


class SubCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration_from = db.Column(db.Date)
    duration_to = db.Column(db.Date)
    remarks = db.Column(db.String(200))
    type = db.Column(db.String(50))
    teachers = db.relationship('TeacherCourse', backref='subcourse', lazy=True)
    attendances = db.relationship('Attendance', backref='subcourse', lazy=True)
    fees = db.relationship('Fee', backref='subcourse', lazy=True)
    student_courses = db.relationship('StudentCourse', backref='subcourse', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(6), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    father_name = db.Column(db.String(50), nullable=False)
    qualification = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    session = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    street = db.Column(db.String(100))
    town = db.Column(db.String(50))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    zipcode = db.Column(db.String(10))
    cnic = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    primary_contact = db.Column(db.String(20))
    gender = db.Column(db.String(10), nullable=False)
    reference_name = db.Column(db.String(50))
    reference_contact = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subcourse_id = db.Column(db.Integer, db.ForeignKey('sub_course.id'), nullable=False)
    remarks = db.Column(db.String(200))
    status_id = db.Column(db.Integer, default=1)  # Default to 1 (new query)
    admission_date = db.Column(db.Date, default=date.today, nullable=False)
    course = db.relationship('Course', backref=db.backref('students', lazy=True))
    subcourse = db.relationship('SubCourse', backref=db.backref('students', lazy=True))
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    fees = db.relationship('Fee', backref='student', lazy=True)
    student_courses = db.relationship('StudentCourse', backref='student', lazy=True)

class StudentCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subcourse_id = db.Column(db.Integer, db.ForeignKey('sub_course.id'), nullable=False)
    date_assigned = db.Column(db.Date, default=datetime.utcnow)



class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    cnic = db.Column(db.String(15), nullable=False, unique=True)
    education = db.Column(db.String(20), nullable=False)
    degree_name = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False, unique=True)
    teacher_courses = db.relationship('TeacherCourse', backref='teacher', lazy=True)
    
class TeacherCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subcourse_id = db.Column(db.Integer, db.ForeignKey('sub_course.id'), nullable=False)
    date_assigned = db.Column(db.Date, default=datetime.utcnow)

    # teacher = db.relationship('Teacher', back_populates='teacher_courses')
    # course = db.relationship('Course')
    # sub_course = db.relationship('SubCourse')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    subcourse_id = db.Column(db.Integer, db.ForeignKey('sub_course.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    
class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subcourse_id = db.Column(db.Integer, db.ForeignKey('sub_course.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    fee_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, nullable=True)
    discount_percentage = db.Column(db.Float, nullable=True)
    net_fee = db.Column(db.Float, nullable=False)
    installment_type = db.Column(db.String(10), nullable=False)
    year = db.Column(db.String(10), nullable=True)
    month = db.Column(db.String(10), nullable=True)
    payment_made = db.Column(db.Float, nullable=True)
    other_charges = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    admission_fee = db.Column(db.Float, nullable=True)
    admission_discount = db.Column(db.Float, nullable=True)
    balance_admission_fee = db.Column(db.Float, nullable=True)
    

    
# Create the tables
# Login manager setup
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for user authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Validate current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('change_password'))

        # Validate new password
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('change_password'))

        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('change_password'))

    return render_template('change_password.html')

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            has_permission = any(
                permission.name == permission_name 
                for role in current_user.roles 
                for permission in role.permissions
            )
            
            if not has_permission:
                flash('You do not have permission to access this resource.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Admin dashboard route with RBAC
@app.route('/admin/dashboard')
@login_required
@permission_required('admin_dashboard')
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

# Create user route (accessible to admin)

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
@permission_required('create_user')
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_ids = request.form.getlist('roles')
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        for role_id in role_ids:
            role = Role.query.get(role_id)
            new_user.roles.append(role)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    roles = Role.query.all()
    return render_template('create_user.html', roles=roles)

# Reset password route (accessible to admin)
@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@permission_required('reset_password')
def reset_password(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        new_password = request.form.get('password')
        user.set_password(new_password)
        db.session.commit()
        flash('Password reset successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('reset_password.html', user=user)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required

def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Update user fields based on form input
        user.username = request.form['username']
        user.email = request.form['email']
        
        # Example: Update password if a new one is provided
        new_password = request.form['new_password']
        if new_password:
            user.set_password(new_password)
        
        # Example: Update roles if applicable in your application
        role_ids = request.form.getlist('roles')
        user.roles.clear()  # Clear existing roles
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)
        
        # Commit changes to the database
        db.session.commit()
        flash('User profile updated successfully.', 'success')
        return redirect(url_for('edit_user', user_id=user.id))
    
    roles = Role.query.all()
    return render_template('edit_user.html', user=user, roles=roles)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/create_role', methods=['GET', 'POST'])
@login_required
@permission_required('create_role')
def create_role():
    role_id = request.args.get('role_id')
    role = None
    if role_id:
        role = Role.query.get(role_id)
    
    if request.method == 'POST':
        role_name = request.form['role_name']
        if role:
            role.name = role_name
            flash('Role updated successfully', 'success')
        else:
            new_role = Role(name=role_name)
            db.session.add(new_role)
            flash('Role created successfully', 'success')
        db.session.commit()
        return redirect(url_for('create_role'))

    roles = Role.query.all()
    return render_template('create_role.html', roles=roles, role=role)

@app.route('/delete_role/<int:role_id>', methods=['GET', 'POST'])
@login_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully', 'success')
    return redirect(url_for('create_role'))


@app.route('/assign_permissions', methods=['GET', 'POST'])
@login_required
@permission_required('assign_permissions')
def assign_permissions():
    if request.method == 'POST':
        role_id = request.form.get('role_id')
        permission_ids = request.form.getlist('permission_ids')
        role = Role.query.get(role_id)
        role.permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        db.session.commit()
        flash('Permissions assigned successfully!', 'success')
        return redirect(url_for('assign_permissions'))
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('assign_permissions.html', roles=roles, permissions=permissions)

def add_permissions():
    permissions = [
        'categories','create_user', 'delete_category', 'subcategories', 'delete_subcategory', 'status',
        'delete_status', 'queries', 'query', 'delete_query', 'proceed_query', 'students',
        'delete_student', 'link_student_course', 'view_student_links', 'view_student',
        'courses', 'delete_course', 'subcourses', 'delete_subcourse', 'teachers', 'delete_teacher',
        'link_teacher_course', 'view_teacher_links', 'attendance', 'edit_attendance',
        'delete_attendance', 'get_subcourses', 'get_students', 'fee_selection', 'fee_form',
        'get_fee', 'create_role', 'assign_permissions', 'admin_dashboard'
    ]
    for permission in permissions:
        if not Permission.query.filter_by(name=permission).first():
            db.session.add(Permission(name=permission))
    db.session.commit()

@app.route('/add_permissions')
def trigger_add_permissions():
    add_permissions()
    return "Permissions added successfully!"


# Home route
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/categories.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('categories')
def categories():
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        name = request.form['name']
        description = request.form['description']

        if category_id:
            category = Category.query.get(category_id)
            if category:
                category.name = name
                category.description = description
                db.session.commit()
                flash('Category updated successfully!', 'success')
            else:
                flash('Category not found!', 'error')
        else:
            new_category = Category(name=name, description=description)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')

        return redirect(url_for('categories'))

    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

# Delete Category
@app.route('/delete_category/<int:category_id>', methods=['POST'])
# @login_required
# @permission_required('delete_category')
def delete_category(category_id):
    subcategory = SubCategory.query.filter_by(category_id=category_id).first()
    if subcategory:
        flash('Cannot delete category as it is tagged with subcategories!', 'error')
    else:
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            flash('Category deleted successfully!', 'success')
        else:
            flash('Category not found!', 'error')
    return redirect(url_for('categories'))
#Subcategory Fucntiona
@app.route('/sub_category.html', methods=['GET', 'POST'])
@app.route('/subcategories/<int:subcategory_id>', methods=['GET', 'POST'])
# @login_required
# @permission_required('subcategories')
def subcategories(subcategory_id=None):
    error = None
    subcategory = None
    categories = Category.query.all()

    if subcategory_id:  # Fetch subcategory details for edit mode
        subcategory = SubCategory.query.get_or_404(subcategory_id)

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        name = request.form.get('name').strip()
        description = request.form.get('description').strip()

        if not name:
            error = "Name is required."
        elif not category_id:
            error = "Category is required."
        else:
            if subcategory:  # Edit operation
                subcategory.category_id = category_id
                subcategory.name = name
                subcategory.description = description
                flash('Subcategory updated successfully', 'success')
            else:  # Add operation
                new_subcategory = SubCategory(category_id=category_id, name=name, description=description)
                db.session.add(new_subcategory)
                flash('Subcategory added successfully', 'success')

            db.session.commit()
            return redirect(url_for('subcategories'))

    all_subcategories = SubCategory.query.all()
    return render_template('sub_category.html', subcategory=subcategory, categories=categories,
                           all_subcategories=all_subcategories, error=error)

@app.route('/delete_subcategory/<int:subcategory_id>', methods=['POST'])
# @login_required
# @permission_required('delete_subcategory')
def delete_subcategory(subcategory_id):
    subcategory = SubCategory.query.get_or_404(subcategory_id)
    try:
        db.session.delete(subcategory)
        db.session.commit()
        flash('Subcategory deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting subcategory: ' + str(e), 'danger')
    return redirect(url_for('subcategories'))

# status Fucntion
@app.route('/status.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('status')
def status():
    if request.method == 'POST':
        status_id = request.form.get('status_id')
        name = request.form['name']
        
        if status_id:
            status = Status.query.get(status_id)
            if status:
                status.name = name
                
                db.session.commit()
                flash('Status updated successfully!', 'success')
            else:
                flash('Status not found!', 'error')
        else:
            new_status = Status(name=name)
            db.session.add(new_status)
            db.session.commit()
            flash('Status added successfully!', 'success')

        return redirect(url_for('status'))

    statuses = Status.query.all()
    return render_template('status.html', statuses=statuses)

# Delete Status
@app.route('/delete_status/<int:status_id>', methods=['POST'])
# @login_required
# @permission_required('delete_status')
def delete_status(status_id):
    query = Query.query.filter_by(status_id=status_id).first()
    if query:
        flash('Cannot delete query as it is tagged with other forms data!', 'error')
    else:
        status = Status.query.get(status_id)
        if status:
            db.session.delete(status)
            db.session.commit()
            flash('Status deleted successfully!', 'success')
        else:
            flash('Status not found!', 'error')
    return redirect(url_for('status'))


# Query form New Function for edit and
@app.route('/query_form.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('queries')
def queries():
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    statuses = Status.query.all()
    query_id = request.args.get('query_id')
    query = None

    if query_id:
        query = Query.query.get(query_id)

    if request.method == 'POST':
        subcategory_id = request.form.get('subcategory_id')
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        address = request.form.get('address').strip()
        phone1 = request.form.get('phone1').strip()
        phone2 = request.form.get('phone2').strip()
        mobile = request.form.get('mobile').strip()
        remarks = request.form.get('remarks').strip()
        date = request.form.get('date')
        status_id = request.form.get('status_id')

        if query:  # Edit operation
            query.subcategory_id = subcategory_id
            query.name = name
            query.email = email
            query.address = address
            query.phone1 = phone1
            query.phone2 = phone2
            query.mobile = mobile
            query.remarks = remarks
            query.date = date
            query.status_id = 1
            db.session.commit()
            flash('Query updated successfully', 'success')
        else:  # Add operation
            new_query = Query(
                subcategory_id=subcategory_id, name=name, email=email,
                address=address, phone1=phone1, phone2=phone2,
                mobile=mobile, remarks=remarks, date=date, status_id=1
            )
            db.session.add(new_query)
            db.session.commit()
            flash('Query added successfully', 'success')

        return redirect(url_for('queries'))

    return render_template('query_form.html', query=query, categories=categories, subcategories=subcategories, statuses=statuses)

@app.route('/query.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('query')
def query():
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    statuses = Status.query.all()

    all_queries = Query.query.all()
    return render_template('query.html', queries=all_queries, categories=categories, subcategories=subcategories, statuses=statuses)

@app.route('/delete_query/<int:query_id>', methods=['POST'])
# @login_required
# @permission_required('delete_query')
def delete_query(query_id):
    query = Query.query.get_or_404(query_id)
    try:
        db.session.delete(query)
        db.session.commit()
        flash('Query deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting query: ' + str(e), 'danger')
    return redirect(url_for('query'))

@app.route('/proceed_query/<int:query_id>', methods=['POST'])
# @login_required
# @permission_required('proceed_query')
def proceed_query(query_id):
    query = Query.query.get_or_404(query_id)
    query.status_id = 2
    db.session.commit()
    flash('Query status updated to Proceed!', 'success')
    return redirect(url_for('students'))

# Student CRUD
@app.route('/students', methods=['GET', 'POST'])
# @login_required
# @permission_required('students')
def students():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        if student_id:  # Edit operation
            student = Student.query.get(student_id)
            if student:
                student.name = request.form['name']
                student.father_name = request.form['father_name']
                student.qualification = request.form['qualification']
                student.age = request.form['age']
                student.session = request.form['session']
                student.dob = request.form['dob']
                student.street = request.form['street']
                student.town = request.form['town']
                student.city = request.form['city']
                student.country = request.form['country']
                student.zipcode = request.form['zipcode']
                student.cnic = request.form['cnic']
                student.email = request.form['email']
                student.phone = request.form['phone']
                student.mobile = request.form['mobile']
                student.primary_contact = request.form['primary_contact']
                student.gender = request.form['gender']
                student.reference_name = request.form['reference_name']
                student.reference_contact = request.form['reference_contact']
                student.remarks = request.form['remarks']
                student.status_id = request.form['status_id']
                student.admission_date = request.form['admission_date']
                db.session.commit()
                flash('Student updated successfully', 'success')
        else:  # Add operation
            new_student = Student(
                name=request.form['name'],
                father_name=request.form['father_name'],
                qualification=request.form['qualification'],
                age=request.form['age'],
                session=request.form['session'],
                dob=request.form['dob'],
                street=request.form['street'],
                town=request.form['town'],
                city=request.form['city'],
                country=request.form['country'],
                zipcode=request.form['zipcode'],
                cnic=request.form['cnic'],
                email=request.form['email'],
                phone=request.form['phone'],
                mobile=request.form['mobile'],
                primary_contact=request.form['primary_contact'],
                gender=request.form['gender'],
                reference_name=request.form['reference_name'],
                reference_contact=request.form['reference_contact'],
                remarks=request.form['remarks'],
                status_id=request.form['status_id'],
                admission_date=request.form['admission_date']
            )
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully', 'success')
        return redirect(url_for('view_student'))
    # Handle search parameters
    
    
    students = Student.query.all()
    return render_template('students.html', students=students)


@app.route('/delete_student/<int:student_id>', methods=['POST'])
# @login_required
# @permission_required('delete_student')
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully', 'success')
    return redirect(url_for('students'))

@app.route('/link_student_course', methods=['GET', 'POST'])
# @login_required
# @permission_required('link_student_course')
def link_student_course():
    students = Student.query.all()
    courses = Course.query.all()
    sub_courses = SubCourse.query.all()
    error = None

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        subcourse_id = request.form.get('subcourse_id')

        if not student_id or not course_id or not subcourse_id:
            error = "All fields are required."
        else:
            new_link = StudentCourse(student_id=student_id, course_id=course_id, subcourse_id=subcourse_id)
            db.session.add(new_link)
            db.session.commit()
            flash('Student linked to course and subcourse successfully', 'success')
            return redirect(url_for('link_student_course'))

    return render_template('link_student_course.html', students=students, courses=courses, sub_courses=sub_courses, error=error)

@app.route('/view_student_links')
# @login_required
# @permission_required('view_student_links')
def view_student_links():
    student_courses = StudentCourse.query.all()
    return render_template('view_student_links.html', student_courses=student_courses)


@app.route('/view_students.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('view_students')
def view_student():
    # Fetch search criteria and term from request
    search_by = request.args.get('search_by')
    search_term = request.args.get('search_term')

    # Filter students based on search criteria
    students_query = Student.query
    if search_by and search_term:
        if search_by == 'name':
            students_query = students_query.filter(Student.name.ilike(f"%{search_term}%"))
        elif search_by == 'father_name':
            students_query = students_query.filter(Student.father_name.ilike(f"%{search_term}%"))
        elif search_by == 'cnic':
            students_query = students_query.filter(Student.cnic.ilike(f"%{search_term}%"))
        elif search_by == 'mobile':
            students_query = students_query.filter(Student.mobile.ilike(f"%{search_term}%"))
        elif search_by == 'email':
            students_query = students_query.filter(Student.email.ilike(f"%{search_term}%"))

    students = students_query.all()
    return render_template('view_students.html', students=students)

# Course CRUD

@app.route('/courses', methods=['GET', 'POST'])
# @login_required
# @permission_required('courses')
def courses():
    error = None
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        name = request.form.get('name').strip()

        if not name:
            error = "Course name is required."
        else:
            if course_id:
                course = Course.query.get_or_404(course_id)
                course.name = name
                flash('Course updated successfully', 'success')
            else:
                new_course = Course(name=name)
                db.session.add(new_course)
                flash('Course added successfully', 'success')
            db.session.commit()
            return redirect(url_for('courses'))

    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses, error=error)

@app.route('/delete_course/<int:course_id>', methods=['POST'])
# @login_required
# @permission_required('delete_course')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting course: ' + str(e), 'danger')
    return redirect(url_for('courses'))


# Subcourse CRUD
# SubCourses CRUD
@app.route('/subcourses.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('subcourses')
def subcourses():
    if request.method == 'POST':
        subcourse_id = request.form.get('subcourse_id')
        course_id = request.form.get('course_id')
        name = request.form.get('name')
        duration_from = request.form.get('duration_from')
        duration_to = request.form.get('duration_to')
        remarks = request.form.get('remarks')
        type = request.form.get('type')

        if subcourse_id:  # Editing an existing subcourse
            subcourse = SubCourse.query.get(subcourse_id)
            subcourse.course_id = course_id
            subcourse.name = name
            subcourse.duration_from = duration_from
            subcourse.duration_to = duration_to
            subcourse.remarks = remarks
            subcourse.type = type
        else:  # Adding a new subcourse
            new_subcourse = SubCourse(
                course_id=course_id,
                name=name,
                duration_from=duration_from,
                duration_to=duration_to,
                remarks=remarks,
                type=type
            )
            db.session.add(new_subcourse)

        db.session.commit()
        return redirect(url_for('subcourses'))

    subcourses = SubCourse.query.all()
    courses = Course.query.all()
    return render_template('subcourses.html', subcourses=subcourses, courses=courses)

@app.route('/delete_subcourse/<int:subcourse_id>', methods=['POST'])
# @login_required
# @permission_required('delete_subcourse')
def delete_subcourse(subcourse_id):
    subcourse = SubCourse.query.get_or_404(subcourse_id)
    db.session.delete(subcourse)
    db.session.commit()
    flash('Subcourse deleted successfully!', 'success')
    return redirect(url_for('subcourses'))

# Teachers CRUD
@app.route('/teachers.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('teachers')
def teachers():
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        name = request.form.get('name')
        father_name = request.form.get('father_name')
        cnic = request.form.get('cnic')
        mobile_number = request.form.get('mobile_number')
        education = request.form.get('education')
        degree_name = request.form.get('degree_name')
        experience = request.form.get('experience')
        course_id = request.form.get('course_id')
        subcourse_id = request.form.get('subcourse_id')
        

        if teacher_id:  # Editing an existing teacher
            teacher = Teacher.query.get(teacher_id)
            teacher.name = name
            teacher.father_name = father_name
            teacher.cnic = cnic
            teacher.mobile_number = mobile_number
            teacher.education = education
            teacher.degree_name = degree_name
            teacher.experience = experience
            
        else:  # Adding a new teacher
            new_teacher = Teacher(
                name=name,
                father_name = father_name,
                cnic = cnic,
                mobile_number = mobile_number,
                education = education,
                degree_name = degree_name,
                experience = experience,
            
                
            )
            db.session.add(new_teacher)

        db.session.commit()
        return redirect(url_for('teachers'))

    teachers = Teacher.query.all()
    courses = Course.query.all()
    subcourses = SubCourse.query.all()
    return render_template('teachers.html', teachers=teachers, courses=courses, subcourses=subcourses)

@app.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
# @login_required
# @permission_required('delete_teacher')
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('teachers'))

# Teacher Linking Function

@app.route('/link_teacher_course', methods=['GET', 'POST'])
# @login_required
# @permission_required('link_teacher_course')
def link_teacher_course():
    teachers = Teacher.query.all()
    courses = Course.query.all()
    sub_courses = SubCourse.query.all()
    error = None

    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        course_id = request.form.get('course_id')
        subcourse_id = request.form.get('subcourse_id')

        if not teacher_id or not course_id or not subcourse_id:
            error = "All fields are required."
        else:
            new_link = TeacherCourse(teacher_id=teacher_id, course_id=course_id, subcourse_id=subcourse_id)
            db.session.add(new_link)
            db.session.commit()
            flash('Teacher linked to course and subcourse successfully', 'success')
            return redirect(url_for('link_teacher_course'))

    return render_template('link_teacher_course.html', teachers=teachers, courses=courses, sub_courses=sub_courses, error=error)

@app.route('/view_teacher_links')
# @login_required
# @permission_required('view_teacher_links')
def view_teacher_links():
    teacher_courses = TeacherCourse.query.all()
    return render_template('view_teacher_links.html', teacher_courses=teacher_courses)

# Attendance CRUD
# Student Attendance CRUD
@app.route('/student_attendance.html', methods=['GET', 'POST'])
# @login_required
# @permission_required('student_attendance')
def attendance():
    if request.method == 'POST':
        course_id = request.form['course_id']
        subcourse_id = request.form['subcourse_id']
        attendance_date = request.form['attendance_date']
        
        existing_attendance = Attendance.query.filter_by(course_id=course_id, subcourse_id=subcourse_id, date=attendance_date).all()
        if existing_attendance:
            flash('Attendance already marked for this date!', 'error')
            return redirect(url_for('attendance'))

        for key, value in request.form.items():
            if key.startswith('attendance_'):
                try:
                    student_id = int(key.split('_')[1])
                    status = 'present' if value == 'present' else 'absent'
                    attendance_record = Attendance(
                        student_id=student_id,
                        course_id=course_id,
                        subcourse_id=subcourse_id,
                        date=attendance_date,
                        status=status
                    )
                    db.session.add(attendance_record)
                except (IndexError, ValueError):
                    # Skip keys that don't have the correct format
                    continue
        db.session.commit()
        flash('Attendance saved successfully!', 'success')
        return redirect(url_for('attendance'))

    courses = Course.query.all()
    attendance_records = Attendance.query.all()
    today = date.today().strftime('%Y-%m-%d')
    return render_template('student_attendance.html', courses=courses, attendance_records=attendance_records, today=today)

@app.route('/edit_attendance/<int:attendance_id>', methods=['GET', 'POST'])
# @login_required
# @permission_required('edit_attendance')
def edit_attendance(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    if request.method == 'POST':
        attendance.course_id = request.form['course_id']
        attendance.subcourse_id = request.form['subcourse_id']
        attendance.student_id = request.form['student_id']
        attendance.date = request.form['attendance_date']
        attendance.status = request.form['status']
        db.session.commit()
        flash('Attendance updated successfully!', 'success')
        return redirect(url_for('attendance'))

    courses = Course.query.all()
    subcourses = SubCourse.query.all()
    students = Student.query.all()
    return render_template('edit_attendance.html', attendance=attendance, courses=courses, subcourses=subcourses, students=students)

@app.route('/delete_attendance/<int:attendance_id>', methods=['POST'])
# @login_required
# @permission_required('delete_attendance')
def delete_attendance(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    db.session.delete(attendance)
    db.session.commit()
    flash('Attendance deleted successfully!', 'success')
    return redirect(url_for('attendance'))

@app.route('/get_subcourses/<int:course_id>')


def get_subcourses(course_id):
    subcourses = SubCourse.query.filter_by(course_id=course_id).all()
    subcourses_list = [{'id': sc.id, 'name': sc.name} for sc in subcourses]
    return jsonify({'subcourses': subcourses_list})

@app.route('/get_students/<int:subcourse_id>')
def get_students(subcourse_id):
    students = Student.query.filter_by(subcourse_id=subcourse_id).all()
    students_list = [{'id': s.id, 'name': s.name, 'father_name': s.father_name, 'cnic': s.cnic, 'mobile': s.mobile} for s in students]
    return jsonify({'students': students_list})

# Route to handle the fee entry form submission
@app.route('/fee_selection', methods=['GET', 'POST'])
# @login_required
# @permission_required('fee_selection')
def fee_selection():
    courses = Course.query.all()
    subcourses = SubCourse.query.all()
    return render_template('fee_selection.html', courses=courses, subcourses=subcourses)

@app.route('/fee_form', methods=['GET', 'POST'])
# @login_required
# @permission_required('fee_form')
def fee_form():
    if request.method == 'POST':
        student_id = request.form['student_id']
        subcourse_id = request.form['subcourse_id']
        course_id = request.form['course_id']
        date = request.form['date']
        admission_fee = request.form['admission_fee']
        admission_discount = request.form['admission_discount']
        balance_admission_fee = request.form['balance_admission_fee']
        installment_type = request.form['installment_type']
        fee_amount = request.form['fee_amount']
        discount_amount = request.form['discount_amount']
        discount_percentage = request.form['discount_percentage']
        other_charges = request.form['other_charges']
        
        # month = request.form.get('month')
        # year = request.form.get('year')
        payment_mode = request.form['payment_mode']
        payment_made = request.form['payment_made']
        net_fee = request.form['net_fee']

        
        fee = Fee(
                student_id=student_id,
                subcourse_id=subcourse_id,
                course_id=course_id,
                date=date,
                fee_amount=fee_amount,
                discount_amount=discount_amount,
                discount_percentage=discount_percentage,
                net_fee=net_fee,
                installment_type=installment_type,
                # year=year,
                # month=month,
                payment_made=payment_made,
                
                other_charges=other_charges,
                
                admission_fee=admission_fee,
                admission_discount=admission_discount,
                balance_admission_fee=balance_admission_fee
            )

        db.session.add(fee)
        db.session.commit()
        return redirect(url_for('fee_selection'))

    courses = Course.query.all()
    subcourses = SubCourse.query.all()
    students = Student.query.all()
    fees = Fee.query.all()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('fee_form.html',fees=fees, students=students ,courses=courses, subcourses=subcourses,  today=today)


# Route to fetch existing fee details for editing
@app.route('/get_fee/<int:student_id>', methods=['GET'])
# @login_required
# @permission_required('get_fee')
def get_fee(student_id):
    fee = Fee.query.filter_by(student_id=student_id).first()
    if fee:
        fee_data = {
            'id': fee.id,
            'fee_amount': fee.fee_amount,
            'discount_amount': fee.discount_amount,
            'discount_percentage': fee.discount_percentage,
            'net_fee': fee.net_fee,
            'installment_type': fee.installment_type,
            'year': fee.year,
            'month': fee.month,
            'payment_made': fee.payment_made,
            'other_charges': fee.other_charges,
            'date': fee.date.strftime('%Y-%m-%d'),
            'admission_fee': fee.admission_fee,
            'admission_discount': fee.admission_discount,
            'balance_admission_fee': fee.balance_admission_fee
        }
        return jsonify(fee_data)
    return jsonify(None)



if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    
    app.run(debug=True) 
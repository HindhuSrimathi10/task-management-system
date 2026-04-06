from flask import Flask, request, jsonify, g
from flask_cors import CORS
from config import Config
from models import mongo, init_db, UserModel, TaskModel
from bson import ObjectId
from datetime import datetime
import jwt
from functools import wraps
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize database with error handling
db_initialized = init_db(app)

if not db_initialized:
    print("\n⚠️  WARNING: Running without database connection!")
    print("Some features will not work properly.\n")

# Helper function to serialize ObjectId
def serialize_doc(doc):
    if doc:
        doc['_id'] = str(doc['_id'])
        if 'assigned_to' in doc and isinstance(doc['assigned_to'], ObjectId):
            doc['assigned_to'] = str(doc['assigned_to'])
        if 'assigned_by' in doc and isinstance(doc['assigned_by'], ObjectId):
            doc['assigned_by'] = str(doc['assigned_by'])
    return doc

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = UserModel.find_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            g.current_user = current_user
        except Exception as e:
            return jsonify({'message': f'Token is invalid: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.current_user['role'] != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(*args, **kwargs)
    return decorated

# Health Check Route
@app.route('/api/health', methods=['GET'])
def health_check():
    db_status = "connected" if db_initialized else "disconnected"
    return jsonify({
        'status': 'healthy', 
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })

# Auth Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    if not db_initialized:
        return jsonify({'message': 'Database not connected. Please check MongoDB connection.'}), 500
    
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'message': 'All fields are required!'}), 400
        
        # Check if user exists
        if UserModel.find_by_email(email):
            return jsonify({'message': 'Email already exists!'}), 400
        
        if UserModel.find_by_username(username):
            return jsonify({'message': 'Username already exists!'}), 400
        
        # Create user
        UserModel.create_user(username, email, password, role='employee')
        
        return jsonify({'message': 'Registration successful! Wait for admin approval.'}), 201
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    if not db_initialized:
        return jsonify({'message': 'Database not connected. Please check MongoDB connection.'}), 500
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Username and password required!'}), 400
        
        user = UserModel.find_by_username(username)
        if not user:
            return jsonify({'message': 'Invalid credentials!'}), 401
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'message': 'Invalid credentials!'}), 401
        
        # Check approval for employees
        if user['role'] == 'employee' and not user.get('is_approved', False):
            return jsonify({'message': 'Account pending admin approval!'}), 403
        
        # Generate token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'role': user['role'],
            'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Admin Routes
@app.route('/api/admin/pending-employees', methods=['GET'])
@token_required
@admin_required
def get_pending_employees():
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    employees = UserModel.get_pending_employees()
    employees = [serialize_doc(emp) for emp in employees]
    return jsonify(employees), 200

@app.route('/api/admin/employees', methods=['GET'])
@token_required
@admin_required
def get_all_employees():
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    employees = UserModel.get_all_employees()
    employees = [serialize_doc(emp) for emp in employees]
    return jsonify(employees), 200

@app.route('/api/admin/approve/<user_id>', methods=['PUT'])
@token_required
@admin_required
def approve_employee(user_id):
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    try:
        result = UserModel.approve_employee(user_id)
        if result and result.modified_count > 0:
            return jsonify({'message': 'Employee approved successfully!'}), 200
        return jsonify({'message': 'Employee not found or already approved!'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/tasks', methods=['POST'])
@token_required
@admin_required
def create_task():
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    try:
        data = request.json
        title = data.get('title')
        description = data.get('description')
        assigned_to = data.get('assigned_to')
        
        if not all([title, assigned_to]):
            return jsonify({'message': 'Title and assigned employee required!'}), 400
        
        TaskModel.create_task(
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=g.current_user['_id']
        )
        
        return jsonify({'message': 'Task created successfully!'}), 201
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/tasks', methods=['GET'])
@token_required
@admin_required
def get_all_tasks():
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    tasks = TaskModel.get_all_tasks()
    tasks = [serialize_doc(task) for task in tasks]
    
    # Populate employee names
    for task in tasks:
        user = UserModel.find_by_id(task['assigned_to'])
        task['assigned_to_name'] = user['username'] if user else 'Unknown'
    
    return jsonify(tasks), 200

@app.route('/api/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_stats():
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    total_employees = len(UserModel.get_all_employees())
    pending_employees = len(UserModel.get_pending_employees())
    tasks_summary = TaskModel.get_tasks_summary()
    
    return jsonify({
        'total_employees': total_employees,
        'pending_approvals': pending_employees,
        'tasks_summary': tasks_summary
    }), 200

# Employee Routes
@app.route('/api/employee/tasks', methods=['GET'])
@token_required
def get_my_tasks():
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    if g.current_user['role'] == 'employee':
        tasks = TaskModel.get_tasks_by_user(g.current_user['_id'])
        tasks = [serialize_doc(task) for task in tasks]
        return jsonify(tasks), 200
    elif g.current_user['role'] == 'admin':
        tasks = TaskModel.get_all_tasks()
        tasks = [serialize_doc(task) for task in tasks]
        return jsonify(tasks), 200
    return jsonify({'message': 'Unauthorized'}), 401

@app.route('/api/employee/tasks/<task_id>/status', methods=['PUT'])
@token_required
def update_task_status(task_id):
    if not db_initialized:
        return jsonify({'message': 'Database not connected.'}), 500
    
    if g.current_user['role'] not in ['employee', 'admin']:
        return jsonify({'message': 'Unauthorized'}), 401
    
    data = request.json
    status = data.get('status')
    
    if status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({'message': 'Invalid status!'}), 400
    
    success = TaskModel.update_task_status(task_id, status, g.current_user['_id'])
    
    if success:
        return jsonify({'message': 'Task status updated successfully!'}), 200
    return jsonify({'message': 'Task not found or unauthorized!'}), 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Task Management System Backend")
    print("="*50)
    if db_initialized:
        print("✅ Database: Connected")
    else:
        print("❌ Database: Not Connected")
        print("\n📝 To fix database connection:")
        print("1. Check your .env file has correct MONGO_URI")
        print("2. Verify username and password in MongoDB Atlas")
        print("3. Add your IP to MongoDB Atlas whitelist")
    print(f"📍 Server running on: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)
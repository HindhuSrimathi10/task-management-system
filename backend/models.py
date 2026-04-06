from datetime import datetime
from flask_pymongo import PyMongo
from bson import ObjectId

mongo = PyMongo()

def init_db(app):
    try:
        # Initialize MongoDB
        mongo.init_app(app)
        
        # Test the connection
        mongo.db.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Create indexes for better performance
        mongo.db.users.create_index('email', unique=True)
        mongo.db.users.create_index('username', unique=True)
        
        # Create default admin account if not exists
        if not mongo.db.users.find_one({'role': 'admin'}):
            from bcrypt import hashpw, gensalt
            admin_password = hashpw('admin123'.encode('utf-8'), gensalt())
            mongo.db.users.insert_one({
                'username': 'admin',
                'email': 'admin@task.com',
                'password': admin_password,
                'role': 'admin',
                'is_approved': True,
                'created_at': datetime.utcnow()
            })
            print("✅ Default admin created: username='admin', password='admin123'")
        else:
            print("✅ Admin user already exists")
            
        return True
        
    except Exception as e:
        print(f"❌ MongoDB initialization failed: {e}")
        print("\nPlease check:")
        print("1. Your MONGO_URI in .env file")
        print("2. Username and password are correct")
        print("3. IP address is whitelisted in MongoDB Atlas")
        print("\nYou can still run the app, but database operations will fail!")
        return False

# User model operations
class UserModel:
    @staticmethod
    def create_user(username, email, password, role='employee'):
        try:
            from bcrypt import hashpw, gensalt
            hashed_password = hashpw(password.encode('utf-8'), gensalt())
            result = mongo.db.users.insert_one({
                'username': username,
                'email': email,
                'password': hashed_password,
                'role': role,
                'is_approved': role == 'admin',
                'created_at': datetime.utcnow()
            })
            return result
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def find_by_email(email):
        try:
            return mongo.db.users.find_one({'email': email})
        except:
            return None
    
    @staticmethod
    def find_by_username(username):
        try:
            return mongo.db.users.find_one({'username': username})
        except:
            return None
    
    @staticmethod
    def find_by_id(user_id):
        try:
            return mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def get_pending_employees():
        try:
            return list(mongo.db.users.find({
                'role': 'employee',
                'is_approved': False
            }))
        except:
            return []
    
    @staticmethod
    def get_all_employees():
        try:
            return list(mongo.db.users.find({
                'role': 'employee'
            }))
        except:
            return []
    
    @staticmethod
    def approve_employee(user_id):
        try:
            result = mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_approved': True}}
            )
            return result
        except:
            return None

# Task model operations
class TaskModel:
    @staticmethod
    def create_task(title, description, assigned_to, assigned_by):
        try:
            result = mongo.db.tasks.insert_one({
                'title': title,
                'description': description,
                'assigned_to': ObjectId(assigned_to),
                'assigned_by': ObjectId(assigned_by),
                'status': 'Pending',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            return result
        except Exception as e:
            print(f"Error creating task: {e}")
            return None
    
    @staticmethod
    def get_tasks_by_user(user_id):
        try:
            return list(mongo.db.tasks.find({
                'assigned_to': ObjectId(user_id)
            }).sort('created_at', -1))
        except:
            return []
    
    @staticmethod
    def get_all_tasks():
        try:
            return list(mongo.db.tasks.find().sort('created_at', -1))
        except:
            return []
    
    @staticmethod
    def update_task_status(task_id, status, user_id):
        try:
            result = mongo.db.tasks.update_one(
                {
                    '_id': ObjectId(task_id),
                    'assigned_to': ObjectId(user_id)
                },
                {
                    '$set': {
                        'status': status,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def get_tasks_summary():
        try:
            pipeline = [
                {'$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }}
            ]
            summary = list(mongo.db.tasks.aggregate(pipeline))
            return {item['_id']: item['count'] for item in summary}
        except:
            return {}
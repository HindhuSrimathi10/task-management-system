from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get connection string
uri = os.getenv('MONGO_URI')

print("Testing connection to MongoDB Atlas...")
print(f"Using URI: {uri[:50]}...")  # Only show first 50 chars for security

try:
    # Connect with timeout
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ SUCCESS! Connected to MongoDB Atlas!")
    
    # List databases
    print("\n📊 Available databases:")
    for db in client.list_database_names():
        print(f"  - {db}")
        
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\n🔧 Troubleshooting steps:")
    print("1. Verify your username and password are correct")
    print("2. Check if special characters in password are URL encoded")
    print("3. Go to MongoDB Atlas > Network Access > Add your IP address")
    print("4. Make sure the cluster name is correct (no 'xxxxx' placeholders)")
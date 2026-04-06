import os
from datetime import timedelta

class Config:

    # MongoDB Atlas connection
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://71762333016_db_user:<db_password>@taskmanagementcluster.1iceu7r.mongodb.net/?appName=TaskManagementCluster"
    )

    # JWT configuration
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "super_secure_random_key_123"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # React frontend origin
    CORS_ORIGINS = ["http://localhost:3000"]
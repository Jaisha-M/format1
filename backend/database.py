import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

# Global database client
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

async def connect_to_mongo():
    """Create database connection"""
    global client, database
    
    try:
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable not set")
        
        client = AsyncIOMotorClient(mongo_url)
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Get database
        db_name = os.environ.get('DB_NAME', 'resume_ats')
        database = client[db_name]
        
        # Create indexes for better performance
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Index on upload_date for sorting
        await database.analyses.create_index([("upload_date", -1)])
        
        # Index on file_name for searching
        await database.analyses.create_index("file_name")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Could not create indexes: {str(e)}")

def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return database
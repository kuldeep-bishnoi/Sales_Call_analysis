from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from ..config.settings import MONGODB_URL, DATABASE_NAME

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Connect to the MongoDB database"""
        try:
            cls.client = AsyncIOMotorClient(MONGODB_URL)
            cls.db = cls.client[DATABASE_NAME]
            
            # Verify connection is successful
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {MONGODB_URL}")
            
            # Create indexes for collections
            await cls._create_indexes()
            
            return cls.db
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def _create_indexes(cls):
        """Create indexes for collections"""
        # Create indexes for calls collection
        await cls.db.calls.create_index("call_id", unique=True)
        await cls.db.calls.create_index("upload_date")
        
        # Create indexes for analysis collection
        await cls.db.analysis.create_index("call_id", unique=True)
    
    @classmethod
    async def close(cls):
        """Close the MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_db(cls):
        """Get the database instance"""
        if cls.db is None:
            raise ConnectionError("Database not connected. Call connect() first.")
        return cls.db 
from app.db import db
from app.config import logger

async def init_indexes():
    """Initialize search indexes in MongoDB Atlas."""
    try:
        await db.Text.create_search_index({
            "name": "embedding_vector_index",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 384,
                        "similarity": "cosine"
                    }
                ]
            }
        })
        
        await db.Text.create_index("topic_id")
        await db.Text.create_index("doc_id")
        await db.Docs.create_index("topic_id")
        await db.Topics.create_index("user_id")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        raise
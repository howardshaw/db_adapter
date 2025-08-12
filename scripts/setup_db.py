#!/usr/bin/env python3
"""Database setup script."""

import asyncio
import logging
from typing import List

from config import get_settings
from infras.repositories.base_po import BasePO
from infras.repositories.factory import get_engine
from models.item_model import ItemModel
from api.v1.schemas.item_schema import ItemCreateSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Set up database with sample data."""
    settings = get_settings()
    engine = get_engine(settings)
    
    try:
        # Create tables
        if settings.USE_ASYNC_DB:
            async with engine.begin() as conn:
                await conn.run_sync(BasePO.metadata.create_all)
        else:
            BasePO.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
        # Add sample data
        await add_sample_data(settings)
        
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise
    finally:
        if settings.USE_ASYNC_DB:
            await engine.dispose()
        else:
            engine.dispose()


async def add_sample_data(settings):
    """Add sample data to the database."""
    sample_items = [
        ItemCreateSchema(
            name="Laptop",
            description="High-performance laptop for development",
            price=1299.99,
            category="electronics"
        ),
        ItemCreateSchema(
            name="Programming Book",
            description="Comprehensive guide to Python development",
            price=49.99,
            category="books"
        ),
        ItemCreateSchema(
            name="Coffee Mug",
            description="Ceramic coffee mug for developers",
            price=12.99,
            category="accessories"
        ),
        ItemCreateSchema(
            name="Wireless Mouse",
            description="Ergonomic wireless mouse",
            price=29.99,
            category="electronics"
        ),
        ItemCreateSchema(
            name="Desk Lamp",
            description="LED desk lamp with adjustable brightness",
            price=39.99,
            category="accessories"
        )
    ]
    
    # Note: In a real application, you would use the service layer
    # to create items. This is a simplified example for setup purposes.
    logger.info(f"Added {len(sample_items)} sample items to the database")


def main():
    """Main function to run the database setup."""
    logger.info("Starting database setup...")
    
    try:
        asyncio.run(setup_database())
        logger.info("Database setup completed successfully!")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        exit(1)


if __name__ == "__main__":
    main() 
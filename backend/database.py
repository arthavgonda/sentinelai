from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, Float, Index
from datetime import datetime
from config import settings
import os

db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_async_engine(db_url, echo=False, connect_args=connect_args)
else:
    engine = create_async_engine(db_url, echo=False, pool_size=20, max_overflow=40)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), index=True)
    query_type = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data = Column(JSON)
    correlation_score = Column(Float, default=0.0)
    status = Column(String(50), default="pending")
    
    __table_args__ = (
        Index('idx_query_type', 'query', 'query_type'),
        Index('idx_created_at', 'created_at'),
    )

class APICache(Base):
    __tablename__ = "api_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(512), unique=True, index=True)
    api_name = Column(String(100), index=True)
    response_data = Column(JSON)
    expires_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    hit_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_cache_key', 'cache_key'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_api_name', 'api_name'),
    )

class Correlation(Base):
    __tablename__ = "correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, index=True)
    source_id = Column(String(255), index=True)
    target_id = Column(String(255), index=True)
    source_type = Column(String(100))
    target_type = Column(String(100))
    confidence_score = Column(Float, index=True)
    correlation_type = Column(String(100))
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_profile_id', 'profile_id'),
        Index('idx_confidence', 'confidence_score'),
        Index('idx_source_target', 'source_id', 'target_id'),
    )

class APIMetric(Base):
    __tablename__ = "api_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String(100), index=True)
    endpoint = Column(String(255))
    response_time = Column(Float)
    status_code = Column(Integer)
    success = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_api_timestamp', 'api_name', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
    )

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


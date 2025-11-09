from celery import Celery
from config import settings
from services.orchestrator import APIOrchestrator
from database import AsyncSessionLocal, Profile
from sqlalchemy import select
from datetime import datetime, timedelta
import asyncio

celery_app = Celery(
    "osint_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000
)

@celery_app.task(name="refresh_profile")
def refresh_profile_task(profile_id: int):
    async def _refresh():
        orchestrator = APIOrchestrator()
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Profile).where(Profile.id == profile_id))
            profile = result.scalar_one_or_none()
            
            if profile:
                result_data = await orchestrator.search(profile.query, profile.query_type, profile_id)
                profile.data = result_data
                profile.updated_at = datetime.utcnow()
                await session.commit()
        
        await orchestrator.close()
    
    asyncio.run(_refresh())

@celery_app.task(name="batch_refresh_profiles")
def batch_refresh_profiles_task():
    async def _batch_refresh():
        orchestrator = APIOrchestrator()
        async with AsyncSessionLocal() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=1)
            result = await session.execute(
                select(Profile).where(
                    Profile.updated_at < cutoff_date,
                    Profile.status == "complete"
                ).limit(100)
            )
            profiles = result.scalars().all()
            
            for profile in profiles:
                try:
                    result_data = await orchestrator.search(profile.query, profile.query_type, profile.id)
                    profile.data = result_data
                    profile.updated_at = datetime.utcnow()
                except Exception as e:
                    print(f"Error refreshing profile {profile.id}: {e}")
            
            await session.commit()
        
        await orchestrator.close()
    
    asyncio.run(_batch_refresh())

@celery_app.task(name="cleanup_old_profiles")
def cleanup_old_profiles_task():
    async def _cleanup():
        async with AsyncSessionLocal() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            result = await session.execute(
                select(Profile).where(Profile.created_at < cutoff_date)
            )
            old_profiles = result.scalars().all()
            
            for profile in old_profiles:
                await session.delete(profile)
            
            await session.commit()
    
    asyncio.run(_cleanup())

celery_app.conf.beat_schedule = {
    "batch-refresh-profiles": {
        "task": "batch_refresh_profiles",
        "schedule": 3600.0,
    },
    "cleanup-old-profiles": {
        "task": "cleanup_old_profiles",
        "schedule": 86400.0,
    },
}


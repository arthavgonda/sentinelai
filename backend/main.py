from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import logging
import uvicorn
import time
from contextlib import asynccontextmanager

from config import settings
from database import init_db, Profile, AsyncSessionLocal
from services.orchestrator import orchestrator
from services.correlation import CorrelationEngine
from utils.validators import validate_email, validate_phone, validate_username, validate_name, sanitize_input
from cache import cache_manager
from sqlalchemy import select

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    query: str
    query_type: Optional[str] = None

class SearchResponse(BaseModel):
    profile_id: int
    status: str
    query: str
    query_type: str
    message: str

active_websockets: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await cache_manager.connect()
        logger.info("Cache manager connected")
    except Exception as e:
        logger.warning(f"Cache connection failed: {e}")
    
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise
    
    logger.info("Application started")
    yield
    
    try:
        await orchestrator.close()
    except Exception as e:
        logger.error(f"Error closing orchestrator: {e}")
    
    try:
        await cache_manager.disconnect()
    except Exception as e:
        logger.error(f"Error disconnecting cache: {e}")
    
    logger.info("Application shutdown")

app = FastAPI(
    title="OSINT System",
    description="High-performance OSINT and Threat Actor Profiling System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "OSINT System API", "status": "operational"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "cache": "connected" if cache_manager.redis_client else "disconnected"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "OSINT System is operational",
        "supported_query_types": ["name", "email", "username", "phone"],
        "example_queries": {
            "name": "John Doe",
            "email": "example@email.com",
            "username": "johndoe",
            "phone": "+1234567890"
        },
        "apis_configured": len(orchestrator.clients),
        "status": "ready"
    }

@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest, background_tasks: BackgroundTasks):
    db = AsyncSessionLocal()
    query = sanitize_input(request.query)
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    query_type = request.query_type
    if not query_type:
        if "@" in query:
            is_valid, error = validate_email(query)
            if is_valid:
                query_type = "email"
            else:
                raise HTTPException(status_code=400, detail=error)
        elif any(char.isdigit() for char in query) and len(query.replace("+", "").replace("-", "").replace(" ", "")) >= 10:
            is_valid, error = validate_phone(query)
            if is_valid:
                query_type = "phone"
            else:
                is_valid_name, _ = validate_name(query)
                if is_valid_name:
                    query_type = "name"
                else:
                    query_type = "username"
        else:
            is_valid_name, _ = validate_name(query)
            if is_valid_name and " " in query:
                query_type = "name"
            else:
                is_valid, error = validate_username(query)
                if is_valid:
                    query_type = "username"
                elif is_valid_name:
                    query_type = "name"
                else:
                    raise HTTPException(status_code=400, detail="Unable to determine query type. Please specify query type manually.")
    else:
        if query_type == "email":
            is_valid, error = validate_email(query)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        elif query_type == "phone":
            is_valid, error = validate_phone(query)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        elif query_type == "username":
            is_valid, error = validate_username(query)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        elif query_type == "name":
            is_valid, error = validate_name(query)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
    
    try:
        profile = Profile(
            query=query,
            query_type=query_type,
            status="pending",
            data={}
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        profile_id = profile.id
    except Exception as e:
        logger.error(f"Error creating profile: {e}", exc_info=True)
        try:
            await db.rollback()
        except:
            pass
        try:
            await db.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")
    finally:
        try:
            await db.close()
        except:
            pass
    
    background_tasks.add_task(process_search, profile_id, query, query_type)
    
    return SearchResponse(
        profile_id=profile_id,
        status="pending",
        query=query,
        query_type=query_type,
        message="Search initiated"
    )

async def process_search(profile_id: int, query: str, query_type: str):
    try:
        # Send initial progress update
        total_apis = len(orchestrator.priority_apis) + len(orchestrator.secondary_apis) + len(orchestrator.background_apis)
        await broadcast_progress(profile_id, 0, "Starting search...", 0, total_apis)
        
        async def progress_wrapper(progress, message, completed, total):
            await broadcast_progress(profile_id, progress, message, completed, total)
        
        result = await orchestrator.search(query, query_type, profile_id, progress_callback=progress_wrapper)
        
        db = AsyncSessionLocal()
        try:
            profile_result = await db.execute(select(Profile).where(Profile.id == profile_id))
            profile = profile_result.scalar_one_or_none()
            if profile:
                profile.data = result
                profile.status = "complete"
                if result.get("correlation") and result["correlation"].get("confidence_scores"):
                    profile.correlation_score = sum(result["correlation"]["confidence_scores"].values()) / len(result["correlation"]["confidence_scores"]) if result["correlation"]["confidence_scores"] else 0.0
                await db.commit()
        finally:
            await db.close()
        
        completed_count = len(result.get("completed_apis", []))
        await broadcast_progress(profile_id, 100, "Search complete!", completed_count, total_apis)
        await broadcast_update(profile_id, result)
    except Exception as e:
        logger.error(f"Search processing error: {e}", exc_info=True)
        await broadcast_progress(profile_id, 0, f"Error: {str(e)}", 0, 0)
        db = AsyncSessionLocal()
        try:
            profile_result = await db.execute(select(Profile).where(Profile.id == profile_id))
            profile = profile_result.scalar_one_or_none()
            if profile:
                profile.status = "error"
                profile.data = {"error": str(e)}
                await db.commit()
        except Exception as db_error:
            logger.error(f"Error updating profile status: {db_error}")
        finally:
            await db.close()
        await broadcast_error(profile_id, str(e))

@app.get("/api/profile/{profile_id}")
async def get_profile(profile_id: int):
    db = AsyncSessionLocal()
    try:
        result = await db.execute(select(Profile).where(Profile.id == profile_id))
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "id": profile.id,
            "query": profile.query,
            "query_type": profile.query_type,
            "status": profile.status,
            "data": profile.data,
            "correlation_score": profile.correlation_score,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
            "pending_apis": profile.data.get("pending_apis", []) if profile.data else []
        }
    finally:
        await db.close()

@app.get("/api/profiles")
async def list_profiles(skip: int = 0, limit: int = 50):
    db = AsyncSessionLocal()
    try:
        result = await db.execute(select(Profile).offset(skip).limit(limit).order_by(Profile.created_at.desc()))
        profiles = result.scalars().all()
        
        return {
            "profiles": [
                {
                    "id": p.id,
                    "query": p.query,
                    "query_type": p.query_type,
                    "status": p.status,
                    "created_at": p.created_at.isoformat()
                }
                for p in profiles
            ],
            "total": len(profiles)
        }
    finally:
        await db.close()

@app.websocket("/ws/{profile_id}")
async def websocket_endpoint(websocket: WebSocket, profile_id: int):
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        db = AsyncSessionLocal()
        try:
            result = await db.execute(select(Profile).where(Profile.id == profile_id))
            profile = result.scalar_one_or_none()
            
            if profile and profile.data:
                await websocket.send_json({
                    "type": "update",
                    "profile_id": profile_id,
                    "data": profile.data
                })
        finally:
            await db.close()
        
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)

async def broadcast_progress(profile_id: int, progress: int, message: str, completed: int, total: int):
    progress_message = {
        "type": "progress",
        "profile_id": profile_id,
        "progress": progress,
        "message": message,
        "completed": completed,
        "total": total,
        "timestamp": time.time()
    }
    
    disconnected = []
    for websocket in active_websockets:
        try:
            await websocket.send_json(progress_message)
        except:
            disconnected.append(websocket)
    
    for ws in disconnected:
        if ws in active_websockets:
            active_websockets.remove(ws)

async def broadcast_update(profile_id: int, data: Dict[str, Any]):
    message = {
        "type": "update",
        "profile_id": profile_id,
        "data": data
    }
    
    disconnected = []
    for websocket in active_websockets:
        try:
            await websocket.send_json(message)
        except:
            disconnected.append(websocket)
    
    for ws in disconnected:
        if ws in active_websockets:
            active_websockets.remove(ws)

async def broadcast_error(profile_id: int, error: str):
    message = {
        "type": "error",
        "profile_id": profile_id,
        "error": error
    }
    
    disconnected = []
    for websocket in active_websockets:
        try:
            await websocket.send_json(message)
        except:
            disconnected.append(websocket)
    
    for ws in disconnected:
        if ws in active_websockets:
            active_websockets.remove(ws)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        loop="asyncio"
    )


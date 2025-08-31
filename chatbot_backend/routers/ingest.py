# chatbot_backend/routers/ingest.py

from fastapi import APIRouter, Depends, HTTPException, Request
from models.schemas import IngestEvent
from utils.auth import verify_jwt_token
from utils.db import save_ingest_event

# This must be defined BEFORE you use @router.post(...)
router = APIRouter()

@router.post("/ingest")
async def ingest_event(
    event: IngestEvent,
    request: Request,
    user_data: dict = Depends(verify_jwt_token)  # Decoded JWT payload
):
    """
    Receives message/group activity events from WordPress and stores them.
    JWT in Authorization header must match BACKEND_JWT_SECRET.
    """
    try:
        # Optional: Cross-check JWT user_id/site_id with payload
        if event.user_id_owner != user_data.get("user_id"):
            raise HTTPException(status_code=403, detail="User ID mismatch")

        # Save to DB (or queue, or analytics pipeline)
        save_ingest_event(event)

        return {"success": True, "message": "Event ingested successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, create_session
from app.services.onedrive import onedrive_service
from pydantic import BaseModel
import secrets

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory store for state tokens (use Redis in production)
auth_states = {}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    microsoft_token: dict


@router.get("/login")
async def login():
    """Initiate OAuth flow with Microsoft"""
    state = secrets.token_urlsafe(32)
    auth_states[state] = True
    
    auth_url = onedrive_service.get_auth_url(state=state)
    return {"auth_url": auth_url}


@router.get("/callback")
async def auth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from Microsoft"""
    # Verify state
    if state not in auth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del auth_states[state]
    
    try:
        # Exchange code for tokens
        token_result = onedrive_service.get_token_from_code(code)
        
        # Store tokens in session to avoid JWT truncation
        session_id = create_session(
            microsoft_token=token_result["access_token"],
            refresh_token=token_result.get("refresh_token")
        )
        
        # Create our own access token (much smaller now)
        access_token = create_access_token(
            data={
                "sub": token_result.get("id_token_claims", {}).get("oid", "user"),
                "session_id": session_id
            }
        )
        
        # Redirect to frontend with token
        from app.core.config import settings
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/success?token={access_token}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh Microsoft access token"""
    try:
        token_result = onedrive_service.refresh_token(refresh_token)
        
        # Create new access token
        access_token = create_access_token(
            data={
                "microsoft_token": token_result["access_token"],
                "refresh_token": token_result.get("refresh_token")
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            microsoft_token=token_result
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

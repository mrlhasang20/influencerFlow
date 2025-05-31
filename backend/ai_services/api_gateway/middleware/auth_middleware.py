# backend/ai_services/api_gateway/middleware/auth_middleware.py
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def authenticate_request(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    if credentials.scheme != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    # Simplified hackathon authentication
    return {"user_id": "demo_user", "role": "admin"}

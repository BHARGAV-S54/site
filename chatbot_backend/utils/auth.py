import os
import jwt
from fastapi import HTTPException, Header

JWT_SECRET = os.getenv("BACKEND_JWT_SECRET", "replace_with_secret")
JWT_ALGORITHM = "HS256"

def verify_jwt_token(authorization: str = Header(...)) -> dict:
    """
    Verifies JWT from Authorization header and returns decoded payload.
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid auth header")
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

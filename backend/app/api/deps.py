from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import verify_access_token
from backend.app.models.user import User

# Standard OAuth2 scheme pointing to login route
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_token_from_header_or_cookie(
    request: Request,
    token_header: Optional[str] = Depends(oauth2_scheme)
) -> Optional[str]:
    """Helper to extract token from standard Authorization header OR cookie."""
    if token_header:
        return token_header
    # Fallback to checking cookie
    return request.cookies.get("access_token")


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_header_or_cookie)
) -> User:
    """Dependency to retrieve the currently logged in user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Clean Bearer prefix if it exists in cookie or header value
    if token.startswith("Bearer "):
        token = token[7:]

    email = verify_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure the user is active."""
    # We can check user.is_active if we had it, otherwise just return current_user
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to enforce admin role access."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

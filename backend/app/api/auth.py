from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, GoogleAuthRequest
from app.api.deps import get_current_user
from app.core.rate_limit import auth_rate_limiter
from app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Registers a new user account with secure password hashing."""
    auth_rate_limiter.check(request)
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    hashed_pw = hash_password(req.password)
    user = User(
        name=req.name.strip(),
        email=req.email.lower().strip(),
        password_hash=hashed_pw,
        role="user",
        is_active=True,
        last_login_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.id)
    logger.info(f"New user registered: {user.email}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticates a user and returns a signed JWT access token."""
    auth_rate_limiter.check(request)
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact system administrator."
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.id)
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/google", response_model=TokenResponse)
def google_auth(req: GoogleAuthRequest, request: Request, db: Session = Depends(get_db)):
    """
    Authenticates a user via verified Google ID token.
    Safe Account Linking:
    - If user exists with google_sub -> login.
    - If user exists with matching verified email -> link google_sub and login.
    - If user does not exist -> create new user with auth_provider='google' and login.
    """
    auth_rate_limiter.check(request)
    from app.services.google_auth_service import google_auth_service, GoogleAuthError
    try:
        google_user = google_auth_service.verify_credential(req.credential)
    except GoogleAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    # 1. Check existing user by google_sub
    user = db.query(User).filter(User.google_sub == google_user.sub).first()

    # 2. Check existing user by verified email (Safe Account Linking)
    if not user:
        user = db.query(User).filter(User.email == google_user.email).first()
        if user:
            user.google_sub = google_user.sub
            if not user.avatar_url and google_user.picture:
                user.avatar_url = google_user.picture
            user.email_verified = True
            db.commit()
            db.refresh(user)
            logger.info(f"Linked Google identity to existing user account: {user.email}")

    # 3. Create new user if not found
    if not user:
        user = User(
            name=google_user.name,
            email=google_user.email,
            password_hash=None,
            google_sub=google_user.sub,
            auth_provider="google",
            email_verified=True,
            avatar_url=google_user.picture,
            role="user",
            is_active=True,
            last_login_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user via Google Sign-In: {user.email}")
    else:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated. Contact system administrator."
            )
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)

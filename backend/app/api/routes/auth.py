from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta, datetime
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.core.database import get_collection
import json
import os

router = APIRouter()

# Simple in-memory user store (for demo - replace with database in production)
USERS_FILE = "./users.json"


def load_users():
    """Load users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save users to file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, default=str)


@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    users = load_users()
    
    # Check if user already exists
    for user_id, user in users.items():
        if user["email"] == user_data.email or user["username"] == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
    
    # Create new user
    new_user_id = len(users) + 1
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "id": new_user_id,
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password,
        "created_at": str(datetime.utcnow())
    }
    
    users[str(new_user_id)] = new_user
    save_users(users)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user_id, "email": user_data.email, "username": user_data.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user_id,
            email=user_data.email,
            username=user_data.username,
            created_at=datetime.utcnow()
        )
    )


@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token."""
    users = load_users()
    
    # Find user by email
    user = None
    for user_id, u in users.items():
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"], "username": user["username"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            created_at=datetime.fromisoformat(user["created_at"]) if isinstance(user["created_at"], str) else user["created_at"]
        )
    )

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.schemas import UserRegister, UserLogin, Token, UserResponse
import json
import os

router = APIRouter()

USERS_FILE = "users.json"


def load_users() -> dict:
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users: dict):
    """Save users to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, default=str)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user."""
    users = load_users()
    
    # Check if user already exists
    for uid, user in users.items():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if user["username"] == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    new_user_id = len(users) + 1
    hashed_password = hash_password(user_data.password)
    
    new_user = {
        "id": new_user_id,
        "email": user_data.email,
        "username": user_data.username,
        "password_hash": hashed_password,
        "created_at": str(datetime.utcnow())
    }
    
    users[str(new_user_id)] = new_user
    save_users(users)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(new_user_id),
            "email": user_data.email,
            "username": user_data.username
        }
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=new_user_id,
            email=user_data.email,
            username=user_data.username,
            created_at=datetime.utcnow()
        )
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token."""
    users = load_users()
    
    # Find user by email
    user = None
    for uid, u in users.items():
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "username": user["username"]
        }
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            created_at=datetime.fromisoformat(user["created_at"]) if isinstance(user["created_at"], str) else user["created_at"]
        )
    )

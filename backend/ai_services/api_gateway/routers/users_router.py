from fastapi import APIRouter, Depends, HTTPException
from shared.database import get_db, User
from sqlalchemy.orm import Session
import uuid

router = APIRouter()

@router.post("/users/register")
def register_user(email: str, name: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        hashed_password=password  # Hash in production!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "name": new_user.name}

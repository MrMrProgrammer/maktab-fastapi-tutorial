from fastapi import FastAPI, Depends, HTTPException, Response, status, Request
from pydantic import BaseModel, Field, condecimal, constr, field_validator
from sqlalchemy.orm import Session
from decimal import Decimal
from app import database, models, crud, auth
from typing import List
from app.i18n.locale import translate
from .schemas import LoginRequest
from app.i18n import get_translation

app = FastAPI(title="Expenses API with JWT, User-specific CRUD and i18n")

# DB setup
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Pydantic Schemas ----------
class ExpenseCreate(BaseModel):
    description: constr(min_length=3, max_length=100, strip_whitespace=True) = Field(..., example="Taxi to office")
    amount: condecimal(gt=0, max_digits=10, decimal_places=2) = Field(..., example="15.50")

    @field_validator("description")
    def validate_description(cls, v: str) -> str:
        import re
        pattern = r"^[A-Za-z0-9\s,.'-]+$"
        if not re.match(pattern, v):
            raise ValueError("Description contains invalid characters")
        return v

class Expense(ExpenseCreate):
    id: int

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., example="user1")
    password: constr(min_length=6) = Field(..., example="secret123")

# ---------- Auth Helpers ----------
def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")
    payload = auth.decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# ---------- Register ----------
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db), msg: str = Depends(lambda: translate("user_registered"))):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=translate("username_exists"))
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": msg}

# ---------- Login ----------
@app.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        msg = get_translation(payload.lang, "invalid_credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    access_token = auth.create_access_token({"sub": user.username})
    refresh_token = auth.create_refresh_token({"sub": user.username})
    auth.set_tokens_in_cookies(response, access_token, refresh_token)

    msg = get_translation(payload.lang, "logged_in")
    return {"msg": msg}


# ---------- Refresh ----------
@app.post("/refresh")
def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=translate("invalid_credentials"))
    payload = auth.decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    username = payload.get("sub")
    access_token = auth.create_access_token({"sub": username})
    auth.set_tokens_in_cookies(response, access_token, token)
    return {"msg": translate("access_token_refreshed")}

# ---------- Logout ----------
@app.post("/logout")
def logout(response: Response):
    auth.clear_tokens(response)
    return {"msg": translate("logged_out")}

# ---------- Expense CRUD (User-specific) ----------
@app.post("/expenses", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = crud.create_expense(db, payload.description, payload.amount, owner_id=current_user.id)
    return {"id": expense.id, "description": expense.description, "amount": expense.amount, "msg": translate("expense_created")}

@app.get("/expenses", response_model=List[Expense])
def list_expenses(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_expenses_by_user(db, user_id=current_user.id)

@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    exp = crud.get_expense_by_user(db, expense_id=expense_id, user_id=current_user.id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("expense_not_found"))
    return exp

@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, payload: ExpenseCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated = crud.update_expense_by_user(db, expense_id, current_user.id, payload.description, payload.amount)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("expense_not_found"))
    return updated

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = crud.delete_expense_by_user(db, expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("expense_not_found"))
    return None

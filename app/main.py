from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field, condecimal, constr, field_validator
from sqlalchemy.orm import Session
from decimal import Decimal
from app import crud, models, database

app = FastAPI(title="Expenses API with DB and Validation")

# ---------- DB Setup ----------
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

# ---------- ROUTES ----------
@app.post("/expenses", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, payload.description, payload.amount)

@app.get("/expenses", response_model=list[Expense])
def list_expenses(db: Session = Depends(get_db)):
    return crud.get_expenses(db)

@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    exp = crud.get_expense(db, expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return exp

@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, payload: ExpenseCreate, db: Session = Depends(get_db)):
    updated = crud.update_expense(db, expense_id, payload.description, payload.amount)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return updated

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return None

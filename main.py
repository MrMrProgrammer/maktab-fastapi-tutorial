from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict
from decimal import Decimal
from uuid import uuid4

app = FastAPI(title="In-Memory Expenses API")

# Pydantic models
class ExpenseCreate(BaseModel):
    description: str = Field(..., example="Coffee with client")
    amount: Decimal = Field(..., example="12.50")

class Expense(ExpenseCreate):
    id: int

# In-memory storage: maps int id -> Expense
expenses: Dict[int, Expense] = {}

# Simple incremental ID generator
_next_id = 1
def get_next_id() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid

# Create a new expense (POST)
@app.post("/expenses", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate):
    new_id = get_next_id()
    expense = Expense(id=new_id, **payload.dict())
    expenses[new_id] = expense
    return expense

# Get all expenses (GET)
@app.get("/expenses", response_model=list[Expense], status_code=status.HTTP_200_OK)
def list_expenses():
    return list(expenses.values())

# Get a single expense by id (GET)
@app.get("/expenses/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
def get_expense(expense_id: int):
    exp = expenses.get(expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return exp

# Update an existing expense by id (PUT)
@app.put("/expenses/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
def update_expense(expense_id: int, payload: ExpenseCreate):
    exp = expenses.get(expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    updated = Expense(id=expense_id, **payload.dict())
    expenses[expense_id] = updated
    return updated

# Delete an expense by id (DELETE)
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    if expense_id not in expenses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    del expenses[expense_id]
    return None

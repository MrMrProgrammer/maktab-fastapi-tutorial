from sqlalchemy.orm import Session
from decimal import Decimal
from app import models

# ---------- CREATE ----------
def create_expense(db: Session, description: str, amount: Decimal):
    expense = models.Expense(description=description, amount=amount)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

# ---------- READ ----------
def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def get_expenses(db: Session):
    return db.query(models.Expense).all()

# ---------- UPDATE ----------
def update_expense(db: Session, expense_id: int, description: str, amount: Decimal):
    expense = get_expense(db, expense_id)
    if not expense:
        return None
    expense.description = description
    expense.amount = amount
    db.commit()
    db.refresh(expense)
    return expense

# ---------- DELETE ----------
def delete_expense(db: Session, expense_id: int):
    expense = get_expense(db, expense_id)
    if not expense:
        return None
    db.delete(expense)
    db.commit()
    return expense

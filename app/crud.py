from sqlalchemy.orm import Session
from decimal import Decimal
from app import models

# ---------- Expenses CRUD ----------

def create_expense(db: Session, description: str, amount: Decimal, owner_id: int):
    """Create a new expense for a specific user."""
    expense = models.Expense(description=description, amount=amount, owner_id=owner_id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def get_expenses_by_user(db: Session, user_id: int):
    """Get all expenses belonging to a specific user."""
    return db.query(models.Expense).filter(models.Expense.owner_id == user_id).all()

def get_expense_by_user(db: Session, expense_id: int, user_id: int):
    """Get a specific expense by ID for a specific user."""
    return (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.owner_id == user_id)
        .first()
    )

def update_expense_by_user(db: Session, expense_id: int, user_id: int, description: str, amount: Decimal):
    """Update a specific expense belonging to a specific user."""
    expense = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.owner_id == user_id)
        .first()
    )
    if not expense:
        return None
    expense.description = description
    expense.amount = amount
    db.commit()
    db.refresh(expense)
    return expense

def delete_expense_by_user(db: Session, expense_id: int, user_id: int):
    """Delete a specific expense belonging to a specific user."""
    expense = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.owner_id == user_id)
        .first()
    )
    if not expense:
        return None
    db.delete(expense)
    db.commit()
    return True

# ---------- Users CRUD ----------

def create_user(db: Session, username: str, hashed_password: str):
    """Create a new user."""
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

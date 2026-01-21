from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.core.database import get_db
from app.models.customer import Customer
from app.models.visit import Visit
from app.schemas import CustomerWithVisit, Customer as CustomerSchema
from datetime import datetime

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=List[CustomerWithVisit])
async def get_customers(
    week_number: Optional[int] = Query(None, ge=1, le=4),
    day_of_week: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all customers with optional filters"""
    query = db.query(Customer)
    
    if week_number:
        query = query.filter(Customer.week_number == week_number)
    
    if day_of_week:
        query = query.filter(Customer.day_of_week == day_of_week)
    
    if location:
        query = query.filter(Customer.location == location)
    
    customers = query.all()
    
    # Load visits for each customer
    result = []
    for customer in customers:
        customer_dict = {
            "id": customer.id,
            "name": customer.name,
            "address": customer.address,
            "account_number": customer.account_number,
            "week_number": customer.week_number,
            "week_label": customer.week_label,
            "day_of_week": customer.day_of_week,
            "date": customer.date,
            "location": customer.location,
            "stop_number": customer.stop_number,
            "visits": [
                {
                    "id": v.id,
                    "customer_id": v.customer_id,
                    "status": v.status,
                    "notes": v.notes,
                    "sales_amount": v.sales_amount,
                    "follow_up_required": v.follow_up_required,
                    "follow_up_date": v.follow_up_date,
                    "follow_up_notes": v.follow_up_notes,
                    "visited_at": v.visited_at,
                    "created_at": v.created_at,
                    "updated_at": v.updated_at
                }
                for v in customer.visits
            ]
        }
        result.append(customer_dict)
    
    return result


@router.get("/{customer_id}", response_model=CustomerWithVisit)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer


@router.get("/account/{account_number}", response_model=CustomerWithVisit)
async def get_customer_by_account(account_number: str, db: Session = Depends(get_db)):
    """Get a customer by account number"""
    customer = db.query(Customer).filter(
        Customer.account_number == account_number
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer


@router.get("/week/{week_number}/day/{day_of_week}", response_model=List[CustomerWithVisit])
async def get_customers_by_week_and_day(
    week_number: int,
    day_of_week: str,
    db: Session = Depends(get_db)
):
    """Get all customers for a specific week and day"""
    customers = db.query(Customer).filter(
        and_(
            Customer.week_number == week_number,
            Customer.day_of_week == day_of_week
        )
    ).order_by(Customer.stop_number).all()
    
    return customers

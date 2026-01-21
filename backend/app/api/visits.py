from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.customer import Customer
from app.models.visit import Visit
from app.schemas import (
    Visit as VisitSchema,
    VisitCreate,
    VisitUpdate,
    DashboardStats
)

router = APIRouter(prefix="/visits", tags=["visits"])


@router.get("/", response_model=List[VisitSchema])
async def get_visits(db: Session = Depends(get_db)):
    """Get all visits"""
    visits = db.query(Visit).all()
    return visits


@router.get("/customer/{customer_id}", response_model=List[VisitSchema])
async def get_customer_visits(customer_id: int, db: Session = Depends(get_db)):
    """Get all visits for a specific customer"""
    visits = db.query(Visit).filter(Visit.customer_id == customer_id).all()
    return visits


@router.post("/", response_model=VisitSchema)
async def create_visit(visit: VisitCreate, db: Session = Depends(get_db)):
    """Create a new visit"""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == visit.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Set visited_at if status is not "not_visited"
    visited_at = None
    if visit.status != "not_visited":
        visited_at = datetime.utcnow()
    
    db_visit = Visit(
        customer_id=visit.customer_id,
        status=visit.status,
        notes=visit.notes,
        sales_amount=visit.sales_amount,
        follow_up_required=visit.follow_up_required,
        follow_up_date=visit.follow_up_date,
        follow_up_notes=visit.follow_up_notes,
        visited_at=visited_at
    )
    
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    
    return db_visit


@router.patch("/{visit_id}", response_model=VisitSchema)
async def update_visit(
    visit_id: int,
    visit_update: VisitUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing visit"""
    db_visit = db.query(Visit).filter(Visit.id == visit_id).first()
    
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    # Update fields
    update_data = visit_update.model_dump(exclude_unset=True)
    
    # Auto-set visited_at if status changes from not_visited
    if "status" in update_data and update_data["status"] != "not_visited":
        if not db_visit.visited_at:
            update_data["visited_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_visit, field, value)
    
    db.commit()
    db.refresh(db_visit)
    
    return db_visit


@router.delete("/{visit_id}")
async def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    """Delete a visit"""
    db_visit = db.query(Visit).filter(Visit.id == visit_id).first()
    
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    db.delete(db_visit)
    db.commit()
    
    return {"message": "Visit deleted successfully"}


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Total customers
    total_customers = db.query(Customer).count()
    
    # Visited count (any status except not_visited)
    visited_count = db.query(Visit).filter(
        Visit.status != "not_visited"
    ).count()
    
    # Sales made count
    sales_made_count = db.query(Visit).filter(
        Visit.status == "sale_made"
    ).count()
    
    # Total sales amount
    total_sales = db.query(func.sum(Visit.sales_amount)).scalar() or 0.0
    
    # Follow-ups required
    follow_ups_required = db.query(Visit).filter(
        Visit.follow_up_required == True
    ).count()
    
    # Week progress (percentage of customers visited per week)
    def calculate_week_progress(week_num):
        week_customers = db.query(Customer).filter(
            Customer.week_number == week_num
        ).count()
        
        if week_customers == 0:
            return 0.0
        
        week_visited = db.query(Visit).join(Customer).filter(
            Customer.week_number == week_num,
            Visit.status != "not_visited"
        ).count()
        
        return (week_visited / week_customers) * 100
    
    return DashboardStats(
        total_customers=total_customers,
        visited_count=visited_count,
        sales_made_count=sales_made_count,
        total_sales_amount=total_sales,
        follow_ups_required=follow_ups_required,
        week_1_progress=calculate_week_progress(1),
        week_2_progress=calculate_week_progress(2),
        week_3_progress=calculate_week_progress(3),
        week_4_progress=calculate_week_progress(4)
    )

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    account_number: str
    week_number: int
    week_label: str
    day_of_week: str
    date: date
    location: str
    stop_number: int


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Visit Schemas
class VisitBase(BaseModel):
    status: str = "not_visited"
    notes: Optional[str] = None
    sales_amount: Optional[float] = 0.0
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None


class VisitCreate(VisitBase):
    customer_id: int


class VisitUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    sales_amount: Optional[float] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    visited_at: Optional[datetime] = None


class Visit(VisitBase):
    id: int
    customer_id: int
    visited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Customer with Visit
class CustomerWithVisit(Customer):
    visits: List[Visit] = []


# Dashboard Stats
class DashboardStats(BaseModel):
    total_customers: int
    visited_count: int
    sales_made_count: int
    total_sales_amount: float
    follow_ups_required: int
    week_1_progress: float
    week_2_progress: float
    week_3_progress: float
    week_4_progress: float


# Sync Response
class SyncResponse(BaseModel):
    success: bool
    message: str
    customers_synced: int
    last_sync: datetime

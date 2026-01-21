from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Visit status
    status = Column(String, default="not_visited")  
    # Options: not_visited, no_contact, contact_made, sale_made, follow_up_required
    
    # Visit details
    visited_at = Column(DateTime)
    notes = Column(Text)
    sales_amount = Column(Float, default=0.0)
    
    # Follow-up tracking
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="visits")

    def __repr__(self):
        return f"<Visit(customer_id={self.customer_id}, status={self.status})>"

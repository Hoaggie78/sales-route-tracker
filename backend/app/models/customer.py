from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    account_number = Column(String, unique=True, index=True)
    
    # Week and day information
    week_number = Column(Integer)  # 1-4
    week_label = Column(String)  # "WEEK 1", "WEEK 2", etc.
    day_of_week = Column(String)  # "MONDAY", "TUESDAY", etc.
    date = Column(Date)  # The actual date
    location = Column(String)  # MCKINLEYVILLE, ARCATA, etc.
    stop_number = Column(Integer)  # 1-10
    
    # Visit tracking relationships
    visits = relationship("Visit", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(name={self.name}, account={self.account_number})>"

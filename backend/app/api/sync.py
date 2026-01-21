from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import tempfile
import os

from app.core.database import get_db
from app.core.security import decode_access_token, get_session
from app.models.customer import Customer
from app.models.visit import Visit
from app.services.onedrive import onedrive_service
from app.services.excel_parser import parse_excel_route_plan, export_tracking_data
from app.schemas import SyncResponse
from app.core.config import settings

router = APIRouter(prefix="/sync", tags=["sync"])


def get_microsoft_token(authorization: str = Header(...)):
    """Extract Microsoft token from JWT"""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization[7:] # Remove 'Bearer ' or 'bearer '
    print(f"RECEIVED TOKEN LENGTH: {len(token)}")
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session_id = payload.get("session_id")
    if not session_id:
        # Fallback for old tokens during transition
        microsoft_token = payload.get("microsoft_token")
    else:
        session = get_session(session_id)
        if not session:
             raise HTTPException(status_code=401, detail="Session expired or invalid")
        microsoft_token = session.get("microsoft_token")

    if not microsoft_token:
        raise HTTPException(status_code=401, detail="Microsoft token not found")
    
    return microsoft_token


@router.post("/upload", response_model=SyncResponse)
async def upload_route_plan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Directly upload a route plan Excel file and save to Supabase"""
    print(f"DEBUG: Received upload request for file: {file.filename}")
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Parse Excel file using existing logic
            customers_data = parse_excel_route_plan(tmp_path)
            
            # Clear existing data
            db.query(Visit).delete()
            db.query(Customer).delete()
            
            # Insert new customers
            customers_count = 0
            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.add(customer)
                customers_count += 1
            
            db.commit()
            
            return SyncResponse(
                success=True,
                message=f"Successfully imported {customers_count} customers from file",
                customers_synced=customers_count,
                last_sync=datetime.utcnow()
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/download")
async def download_tracking_data(db: Session = Depends(get_db)):
    """Generate and return a tracking Excel file for download"""
    try:
        # Get all customers with their latest visits (existing logic reused)
        customers = db.query(Customer).all()
        
        customers_data = []
        for customer in customers:
            latest_visit = db.query(Visit).filter(
                Visit.customer_id == customer.id
            ).order_by(Visit.updated_at.desc()).first()
            
            customer_dict = {
                "name": customer.name,
                "address": customer.address,
                "account_number": customer.account_number,
                "week_number": customer.week_number,
                "week_label": customer.week_label,
                "day_of_week": customer.day_of_week,
                "date": customer.date,
                "location": customer.location,
                "stop_number": customer.stop_number,
                "latest_visit": {
                    "status": latest_visit.status if latest_visit else "not_visited",
                    "visited_at": latest_visit.visited_at if latest_visit else None,
                    "notes": latest_visit.notes if latest_visit else "",
                    "sales_amount": latest_visit.sales_amount if latest_visit else 0.0,
                    "follow_up_required": latest_visit.follow_up_required if latest_visit else False,
                    "follow_up_date": latest_visit.follow_up_date if latest_visit else None
                }
            }
            customers_data.append(customer_dict)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Export to Excel
            export_tracking_data(customers_data, tmp_path)
            
            # Generate descriptive filename
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"Route_Tracking_Backup_{today}.xlsx"
            
            return FileResponse(
                path=tmp_path,
                filename=filename,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.post("/import", response_model=SyncResponse)
async def sync_from_onedrive(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Import route plan from OneDrive Excel file"""
    
    try:
        microsoft_token = get_microsoft_token(authorization)
        
        # Download file from OneDrive
        file_content = onedrive_service.get_file_content(
            microsoft_token,
            settings.ONEDRIVE_FILE_PATH
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            # Parse Excel file
            customers_data = parse_excel_route_plan(tmp_path)
            
            # Clear existing customers (if any)
            db.query(Visit).delete()
            db.query(Customer).delete()
            
            # Insert customers
            customers_count = 0
            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.add(customer)
                customers_count += 1
            
            db.commit()
            
            return SyncResponse(
                success=True,
                message=f"Successfully synced {customers_count} customers from OneDrive",
                customers_synced=customers_count,
                last_sync=datetime.utcnow()
            )
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        import traceback
        error_msg = f"DEBUG SYNC ERROR: {str(e)}"
        print(error_msg)
        with open("sync_error.log", "a") as f:
            f.write(f"\n--- {datetime.now()} ---\n")
            f.write(error_msg + "\n")
            f.write(traceback.format_exc() + "\n")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/export", response_model=SyncResponse)
async def sync_to_onedrive(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Export tracking data to OneDrive"""
    
    try:
        microsoft_token = get_microsoft_token(authorization)
        
        # Get all customers with their latest visits
        customers = db.query(Customer).all()
        
        customers_data = []
        for customer in customers:
            latest_visit = db.query(Visit).filter(
                Visit.customer_id == customer.id
            ).order_by(Visit.updated_at.desc()).first()
            
            customer_dict = {
                "name": customer.name,
                "address": customer.address,
                "account_number": customer.account_number,
                "week_number": customer.week_number,
                "week_label": customer.week_label,
                "day_of_week": customer.day_of_week,
                "date": customer.date,
                "location": customer.location,
                "stop_number": customer.stop_number,
                "latest_visit": {
                    "status": latest_visit.status if latest_visit else "not_visited",
                    "visited_at": latest_visit.visited_at if latest_visit else None,
                    "notes": latest_visit.notes if latest_visit else "",
                    "sales_amount": latest_visit.sales_amount if latest_visit else 0.0,
                    "follow_up_required": latest_visit.follow_up_required if latest_visit else False,
                    "follow_up_date": latest_visit.follow_up_date if latest_visit else None
                }
            }
            customers_data.append(customer_dict)
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Export to Excel
            export_tracking_data(customers_data, tmp_path)
            
            # Read file content
            with open(tmp_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to OneDrive
            export_path = settings.ONEDRIVE_FILE_PATH.replace(".xlsx", "_Tracking.xlsx")
            onedrive_service.upload_file_content(
                microsoft_token,
                export_path,
                file_content
            )
            
            return SyncResponse(
                success=True,
                message=f"Successfully exported tracking data to OneDrive",
                customers_synced=len(customers_data),
                last_sync=datetime.utcnow()
            )
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get current sync status"""
    total_customers = db.query(Customer).count()
    total_visits = db.query(Visit).count()
    
    return {
        "total_customers": total_customers,
        "total_visits": total_visits,
        "has_data": total_customers > 0
    }

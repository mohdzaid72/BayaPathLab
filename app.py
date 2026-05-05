from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import os
import shutil
from datetime import datetime
from typing import Optional

from database import SessionLocal, engine
from models import Base, TestPoster, Enquiry, Admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BayaPathLab")

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_admin_exists(db: Session):
    """Ensure admin user exists"""
    try:
        admin_count = db.query(Admin).count()
        if admin_count == 0:
            hashed_password = pwd_context.hash("admin123")
            admin = Admin(username="admin", hashed_password=hashed_password)
            db.add(admin)
            db.commit()
            print("✅ Created default admin: admin/admin123")
    except Exception as e:
        print(f"⚠️ Admin creation error: {e}")
        db.rollback()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        tests = db.query(TestPoster).filter(TestPoster.is_active == True).all()
    except:
        tests = []
    return templates.TemplateResponse("index.html", {"request": request, "tests": tests})

@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Ensure admin exists
        ensure_admin_exists(db)
        
        # Find admin
        admin = db.query(Admin).filter(Admin.username == username).first()
        
        if not admin:
            print(f"❌ Admin not found: {username}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        if not pwd_context.verify(password, admin.hashed_password):
            print(f"❌ Wrong password for: {username}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        print(f"✅ Admin login successful: {username}")
        
        # Create secure response
        response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="admin_session", 
            value=f"{username}_{int(datetime.now().timestamp())}", 
            httponly=True, 
            secure=False,
            samesite="lax",
            max_age=3600
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login server error")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    session = request.cookies.get("admin_session")
    if not session or not session.startswith("admin_"):
        raise HTTPException(status_code=302, headers={"Location": "/admin"})
    
    try:
        tests = db.query(TestPoster).all()
        enquiries = db.query(Enquiry).order_by(Enquiry.created_at.desc()).limit(20).all()
    except:
        tests = []
        enquiries = []
    
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "tests": tests, 
        "enquiries": enquiries,
        "session_valid": True
    })

@app.post("/admin/add-test", response_class=HTMLResponse)
async def add_test(
    request: Request,
    test_name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if request.cookies.get("admin_session", "").startswith("admin_") is False:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Secure filename
        timestamp = int(datetime.now().timestamp())
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = f"uploads/{safe_filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        test = TestPoster(
            test_name=test_name[:100],
            price=price,
            description=description[:500],
            image_path=f"/uploads/{safe_filename}"
        )
        db.add(test)
        db.commit()
        print(f"✅ Added test: {test_name}")
        
    except Exception as e:
        print(f"❌ Add test error: {e}")
        db.rollback()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/delete-test/{test_id}", response_class=HTMLResponse)
async def delete_test(test_id: int, request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("admin_session", "").startswith("admin_") is False:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        test = db.query(TestPoster).filter(TestPoster.id == test_id).first()
        if test:
            file_path = f"uploads/{os.path.basename(test.image_path)}"
            if os.path.exists(file_path):
                os.remove(file_path)
            db.delete(test)
            db.commit()
            print(f"✅ Deleted test ID: {test_id}")
    except Exception as e:
        print(f"❌ Delete error: {e}")
        db.rollback()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/enquiry", response_class=HTMLResponse)
async def submit_enquiry(
    patient_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    test_name: str = Form(""),
    message: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        enquiry = Enquiry(
            patient_name=patient_name[:100],
            phone=phone[:15],
            email=email[:100],
            test_name=test_name[:100],
            message=message[:1000]
        )
        db.add(enquiry)
        db.commit()
        print(f"✅ New enquiry from: {patient_name}")
    except Exception as e:
        print(f"❌ Enquiry error: {e}")
        db.rollback()
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/health")
async def health():
    return {"status": "healthy", "admin": "admin/admin123"}

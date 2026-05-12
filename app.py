from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from passlib.context import CryptContext
import os
import shutil
from datetime import datetime, timedelta
from typing import Optional

from database import SessionLocal, engine
from models import Base, TestPoster, Enquiry, Admin
from pydantic import BaseModel

from llm import get_ai_response

from sqlalchemy import create_engine, Column, Integer, String, DateTime
import uuid
import smtplib
from email.mime.text import MIMEText
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import secrets
import bcrypt

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


"""

print(templates)
@app.get("/")
def test(db: Session = Depends(get_db)):
    
    try:
        tests = db.query(TestPoster).all()
        return {"tests_count": len(tests)}
                
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/test-html", response_class=HTMLResponse)
def test(request: Request):
    return templates.TemplateResponse(
        "demo.html",
        {"request": request}
    )

"""
    
    
    
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        tests = db.query(TestPoster).filter(TestPoster.is_active == True).all()
    except:
        tests = []
    return templates.TemplateResponse("index.html", {"request": request, "tests": tests})

@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})

    # 🚫 Prevent browser caching (IMPORTANT FIX)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response
@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    ensure_admin_exists(db)
    print("PASSWORD TYPE:", type(password))
    print("PASSWORD VALUE:", password)
    print("PASSWORD LENGTH:", len(str(password)))

    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin or not pwd_context.verify(password, admin.hashed_password):
        return RedirectResponse(
            url="/admin",
            status_code=status.HTTP_303_SEE_OTHER
        )

    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="admin_session",
        value=f"{username}_{int(datetime.now().timestamp())}",
        httponly=True,
        samesite="lax"
    )
    return response
    

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    session = request.cookies.get("admin_session")
    if not session:
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
    def get_current_admin(request: Request):
        token = request.cookies.get("admin_session")
        if not token:
            raise HTTPException(401)

        try:
            username = serializer.loads(token, max_age=3600)
            return username
        except:
            raise HTTPException(401)
    
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



# ---- CHAT API ----
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):

    reply = get_ai_response(req.message)

    return {"reply": reply}





# =========================
# EMAIL CONFIG
# =========================

conf = ConnectionConfig(
    MAIL_USERNAME="bayapathlab@gmail.com",
    MAIL_PASSWORD="YOUR_GMAIL_APP_PASSWORD",
    MAIL_FROM="bayapathlab@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

# =========================
# TEMP STORAGE
# =========================

reset_tokens = {}

# Example admin password


# =========================
# LOGIN PAGE
# =========================

@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

# =========================
# FORGOT PASSWORD
# =========================

@app.get("/admin/forgot-password")
async def forgot_password():

    # Generate secure token
    token = secrets.token_urlsafe(32)

    # Save token
    reset_tokens[token] = True

    # Reset link
    reset_link = f"http://127.0.0.1:8000/reset-password/{token}"

    # Email message
    message = MessageSchema(
        subject="Reset Admin Password",
        recipients=["bayapathlab@gmail.com"],
        body=f"""
Click the link below to reset your password:

{reset_link}
""",
        subtype="plain"
    )

    # Send email
    fm = FastMail(conf)
    await fm.send_message(message)

    return {
        "message": "Password reset link sent to admin email"
    }

# =========================
# RESET PASSWORD PAGE
# =========================

@app.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(
    request: Request,
    token: str
):

    if token not in reset_tokens:
        return HTMLResponse(
            "Invalid or expired link",
            status_code=400
        )

    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "token": token
        }
    )

# =========================
# UPDATE PASSWORD
# =========================

@app.post("/reset-password")
async def update_password(
    token: str = Form(...),
    new_password: str = Form(...)
):

    global admin_password_hash

    # Validate token
    if token not in reset_tokens:
        return {
            "error": "Invalid token"
        }

    # Hash new password
    admin_password_hash = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    )

    # Remove token
    del reset_tokens[token]

    return RedirectResponse(
        url="/admin/login",
        status_code=303
    )
    
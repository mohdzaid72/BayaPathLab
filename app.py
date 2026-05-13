import os
import shutil
import secrets

from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Form,
    File,
    UploadFile,
    Request,
    status
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer

from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig
)

from database import SessionLocal, engine
from models import (
    Base,
    TestPoster,
    Enquiry,
    Admin,
    PasswordReset
)

from llm import get_ai_response

# =========================
# LOAD ENV
# =========================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise Exception("SECRET_KEY missing in .env")

# =========================
# APP SETUP
# =========================

app = FastAPI(title="BayaPathLab")

Base.metadata.create_all(bind=engine)

# =========================
# DIRECTORIES
# =========================

os.makedirs("uploads", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# =========================
# STATIC FILES
# =========================

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

# =========================
# SECURITY
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
reset_tokens = {}

serializer = URLSafeTimedSerializer(SECRET_KEY)

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# =========================
# EMAIL CONFIG
# =========================

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

# =========================
# DATABASE
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# SESSION HELPERS
# =========================

def create_session(username: str):
    return serializer.dumps(username)

def verify_session(token: str):
    try:
        username = serializer.loads(
            token,
            max_age=86400
        )
        return username
    except:
        return None

# =========================
# ADMIN CREATION
# =========================

def ensure_admin_exists(db: Session):

    admin = db.query(Admin).first()

    if not admin:

        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        hashed_password = pwd_context.hash(admin_password)

        admin = Admin(
            username=admin_username,
            hashed_password=hashed_password
        )

        db.add(admin)
        db.commit()

        print("✅ Default admin created")

# =========================
# HOME
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: Session = Depends(get_db)
):

    try:
        tests = db.query(TestPoster).filter(
            TestPoster.is_active == True
        ).all()

    except Exception as e:
        print("HOME ERROR:", e)
        tests = []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tests": tests
        }
    )

# =========================
# ADMIN REDIRECT
# =========================

@app.get("/admin")
async def admin_redirect():

    return RedirectResponse(
        url="/admin/login",
        status_code=302
    )

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
# ADMIN LOGIN
# =========================

@app.post("/admin/login")
async def admin_login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    ensure_admin_exists(db)

    admin = db.query(Admin).filter(
        Admin.username == username
    ).first()

    if not admin:

        return RedirectResponse(
            url="/admin/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if not pwd_context.verify(
        password,
        admin.hashed_password
    ):

        return RedirectResponse(
            url="/admin/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    response = RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )

    response.set_cookie(
        key="admin_session",
        value=create_session(username),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400
    )

    return response

# =========================
# LOGOUT
# =========================

@app.get("/admin/logout")
async def logout():

    response = RedirectResponse(
        url="/admin/login",
        status_code=303
    )

    response.delete_cookie("admin_session")

    return response

# =========================
# DASHBOARD
# =========================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    token = request.cookies.get("admin_session")

    if not token or not verify_session(token):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    try:

        tests = db.query(TestPoster).all()

        enquiries = db.query(Enquiry).order_by(
            Enquiry.created_at.desc()
        ).limit(50).all()

    except Exception as e:

        print("DASHBOARD ERROR:", e)

        tests = []
        enquiries = []

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tests": tests,
            "enquiries": enquiries
        }
    )

# =========================
# ADD TEST
# =========================

@app.post("/admin/add-test")
async def add_test(
    request: Request,
    test_name: str = Form(...),
    mrp_price: float = Form(...),   # NEW
    price: float = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    token = request.cookies.get("admin_session")

    if not token or not verify_session(token):

        return RedirectResponse(
            url="/admin/login",
            status_code=303
        )

    try:

        ext = file.filename.split(".")[-1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type"
            )

        if file.content_type not in [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]:
            raise HTTPException(
                status_code=400,
                detail="Invalid image type"
            )

        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large"
            )

        filename = f"{secrets.token_hex(16)}.{ext}"

        file_path = f"uploads/{filename}"

        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        test = TestPoster(
            test_name=test_name[:100],
            mrp_price=mrp_price,   # NEW
            price=price,
            description=description[:1000],
            image_path=f"/uploads/{filename}"
        )

        db.add(test)
        db.commit()

        print(f"✅ Added test: {test_name}")

    except Exception as e:

        print("ADD TEST ERROR:", e)

        db.rollback()

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )

# =========================
# DELETE TEST
# =========================

@app.post("/admin/delete-test/{test_id}")
async def delete_test(
    test_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    token = request.cookies.get("admin_session")

    if not token or not verify_session(token):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    try:

        test = db.query(TestPoster).filter(
            TestPoster.id == test_id
        ).first()

        if test:

            file_path = "." + test.image_path

            if os.path.exists(file_path):
                os.remove(file_path)

            db.delete(test)
            db.commit()

            print(f"✅ Deleted test ID: {test_id}")

    except Exception as e:

        print("DELETE ERROR:", e)

        db.rollback()

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )

# =========================
# ENQUIRY
# =========================

@app.post("/enquiry")
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

        print(f"✅ New enquiry: {patient_name}")

    except Exception as e:

        print("ENQUIRY ERROR:", e)

        db.rollback()

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )

# =========================
# CHATBOT
# =========================

class ChatRequest:
    def __init__(self, message: str):
        self.message = message

@app.post("/chat")
async def chat(request: Request):

    try:

        data = await request.json()

        message = data.get("message", "")

        if not message:
            raise HTTPException(
                status_code=400,
                detail="Message required"
            )

        if len(message) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Message too long"
            )

        reply = get_ai_response(message)

        return JSONResponse({
            "reply": reply
        })

    except Exception as e:

        print("CHAT ERROR:", e)

        return JSONResponse(
            {
                "reply": "Sorry, AI service is temporarily unavailable."
            },
            status_code=500
        )

# =========================
# FORGOT PASSWORD
# =========================

@app.get("/admin/forgot-password")
async def forgot_password(db: Session = Depends(get_db)):

    # ✅ ALWAYS fetch admin safely (NO username dependency)
    admin = db.query(Admin).first()

    if not admin:
        return {"error": "Admin not found in DB"}

    # generate token
    token = secrets.token_urlsafe(32)

    # store using STABLE ID
    reset_tokens[token] = {
        "admin_id": admin.id,
        "expires_at": datetime.utcnow() + timedelta(minutes=15)
    }
    BASE_URL = os.getenv("BASE_URL","http://127.0.0.1:8000")

    reset_link = f"{BASE_URL}/reset-password/{token}"

    

    message = MessageSchema(
        subject="Reset Password",
        recipients=[os.getenv("MAIL_FROM")],
        body=f"""
Click below to reset your password:

{reset_link}

Valid for 15 minutes.
""",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Reset link sent successfully"}

# =========================
# RESET PAGE
# =========================

@app.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_page(request: Request, token: str):

    data = reset_tokens.get(token)

    if not data:
        return HTMLResponse("Invalid or expired token", status_code=400)

    if data["expires_at"] < datetime.utcnow():
        return HTMLResponse("Token expired", status_code=400)

    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "token": token
        }
    )

# =========================
# UPDATE PASSWORD (SAFE ID BASED)
# =========================

@app.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    username: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    data = reset_tokens.get(token)

    if not data:
        return {"error": "Invalid token"}

    if data["expires_at"] < datetime.utcnow():
        return {"error": "Token expired"}

    if new_password != confirm_password:
        return {"error": "Passwords do not match"}

    # ✅ IMPORTANT: USE ID NOT USERNAME
    admin = db.query(Admin).filter(
        Admin.id == data["admin_id"]
    ).first()

    if not admin:
        return {"error": "Admin not found"}

    # username CAN change safely
    admin.username = username

    admin.hashed_password = pwd_context.hash(new_password)

    db.commit()

    # remove token after use
    del reset_tokens[token]

    return RedirectResponse(
        url="/admin/login",
        status_code=303
    )

# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
async def health():
    return {"status": "ok"}
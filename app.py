import os
import secrets
import logging

from fastapi.responses import Response, PlainTextResponse

from datetime import datetime, timedelta

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
import requests
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.concurrency import run_in_threadpool

from sqlalchemy.orm import Session

from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from database import SessionLocal, engine
from models import Base, TestPoster, Enquiry, Admin

from demollm import get_ai_response

# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bayapathlab")

# =========================
# ENV
# =========================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY missing")

ENV = os.getenv("ENV", "development")

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    BASE_URL = (
        "https://www.bayapathlab.com"
        if ENV == "production"
        else "http://127.0.0.1:8000"
    )

# =========================
# APP
# =========================

app = FastAPI(title="BayaPathLab")

Base.metadata.create_all(bind=engine)

# =========================
# FILES
# =========================

os.makedirs("uploads", exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

# =========================
# SECURITY
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(SECRET_KEY)

reset_tokens = {}
RESET_TOKEN_EXPIRE_MINUTES = 15

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

# =========================
# EMAIL
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
# WHATSAPP NOTIFICATION
# =========================

def send_whatsapp_enquiry(enquiry):

    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    admin_number = os.getenv("WHATSAPP_ADMIN_NUMBER")


    if not token or not phone_id or not admin_number:
        logger.warning(
            "WhatsApp configuration missing"
        )
        return


    version = os.getenv(
    "WHATSAPP_API_VERSION",
    "v23.0"
    )

    url = (
        f"https://graph.facebook.com/"
        f"{version}/{phone_id}/messages"
    )


    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


    message = f"""
📩 *New BayaPathLab Enquiry*

👤 Name:
{enquiry.patient_name}

📞 Phone:
{enquiry.phone}

📧 Email:
{enquiry.email or "Not provided"}

🧪 Test:
{enquiry.test_name or "Not mentioned"}

💬 Message:
{enquiry.message or "No message"}
"""


    payload = {

        "messaging_product": "whatsapp",

        "to": admin_number,

        "type": "text",

        "text": {
            "body": message
        }
    }


    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10
        )


        if not response.ok:

            logger.error(
                f"WhatsApp failed: {response.text}"
            )

        else:

            logger.info(
                "WhatsApp enquiry sent"
            )


    except Exception as e:

        logger.exception(
            f"WhatsApp Error: {e}"
        )

# =========================
# DB
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# SESSION
# =========================

def create_session(username: str):
    return serializer.dumps(username)

def verify_session(token: str):
    try:
        return serializer.loads(token, max_age=86400)
    except:
        return None

# =========================
# ADMIN HELPERS
# =========================

def ensure_admin_exists(db: Session):
    admin = db.query(Admin).first()

    if not admin:
        admin = Admin(
            username=os.getenv("ADMIN_USERNAME", "admin"),
            hashed_password=pwd_context.hash(os.getenv("ADMIN_PASSWORD", "admin123"))
        )
        db.add(admin)
        db.commit()
        logger.info("Admin created")

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        ensure_admin_exists(db)
    finally:
        db.close()

# =========================
# CURRENT ADMIN (FIXED AUTH)
# =========================

def get_current_admin(request: Request, db: Session):
    token = request.cookies.get("admin_session")

    if not token:
        return None

    username = verify_session(token)
    if not username:
        return None

    return db.query(Admin).filter(Admin.username == username).first()

# =========================
# HOME
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    tests = db.query(TestPoster).all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tests": tests}
    )
@app.get("/admin")
async def admin(request: Request):
    return RedirectResponse(url="/admin/login", status_code=303)
    

# =========================
# LOGIN PAGE (FORCE LOGOUT)
# =========================

@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):

    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("admin_session")  # 🔥 force logout
    return response

# =========================
# LOGIN
# =========================

@app.post("/admin/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    ensure_admin_exists(db)

    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin or not pwd_context.verify(password, admin.hashed_password):
        return RedirectResponse("/admin/login", status_code=303)

    response = RedirectResponse("/admin/dashboard", status_code=303)

    response.set_cookie(
        key="admin_session",
        value=create_session(username),
        httponly=True,
        secure=ENV == "production",
        samesite="lax",
        max_age=86400
    )

    return response

# =========================
# DASHBOARD (FIXED BYPASS)
# =========================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):

    admin = get_current_admin(request, db)

    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    tests = db.query(TestPoster).all()
    enquiries = db.query(Enquiry).order_by(Enquiry.id.desc()).limit(50).all()

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "tests": tests, "enquiries": enquiries}
    )

# =========================
# ADD TEST
# =========================

@app.post("/admin/add-test")
async def add_test(
    request: Request,
    test_name: str = Form(...),
    mrp_price: float = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    ext = file.filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Invalid image type")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    filename = f"{secrets.token_hex(16)}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    test = TestPoster(
        test_name=test_name[:100],
        mrp_price=mrp_price,
        price=price,
        description=description[:1000],
        image_path=f"/uploads/{filename}"
    )

    db.add(test)
    db.commit()

    logger.info("Test added")

    return RedirectResponse("/admin/dashboard", status_code=303)

# =========================
# DELETE TEST (FIXED)
# =========================
@app.post("/admin/delete-test/{test_id}")
async def delete_test(
    test_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    test = db.query(TestPoster).filter(TestPoster.id == test_id).first()

    if not test:
        raise HTTPException(404, "Test not found")

    # delete image file safely
    if test.image_path:
        try:
            file_path = os.path.join(UPLOAD_DIR, os.path.basename(test.image_path))
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"File delete failed: {e}")

    db.delete(test)
    db.commit()

    return RedirectResponse("/admin/dashboard", status_code=303)

# =========================
# CHATBOT (NON BLOCKING)
# =========================

@app.post("/chat")
async def chat(request: Request):

    data = await request.json()
    message = data.get("message", "")

    if not message:
        raise HTTPException(400, "Message required")

    reply = await run_in_threadpool(get_ai_response, message)

    return JSONResponse({"reply": reply})

# =========================
# FORGOT PASSWORD
# =========================

@app.get("/admin/forgot-password")
async def forgot_password(db: Session = Depends(get_db)):
    try:
        admin = db.query(Admin).first()

        token = secrets.token_urlsafe(32)

        reset_tokens[token] = {
            "admin_id": admin.id,
            "expires_at": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        }

        link = f"{BASE_URL}/reset-password/{token}"

        message = MessageSchema(
            subject="Reset Password",
            recipients=[os.getenv("MAIL_FROM")],
            body=f"Reset link:\n\n{link}",
            subtype="plain"
        )

        await FastMail(conf).send_message(message)

        return {"message": "sent"}

    except Exception as e:
        logger.exception("Forgot password error")
        return {"error": str(e)}
# =========================
# RESET PAGE
# =========================

@app.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_page(request: Request, token: str):

    data = reset_tokens.get(token)

    if not data or data["expires_at"] < datetime.utcnow():
        return HTMLResponse("Invalid/Expired", status_code=400)

    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": token}
    )

# =========================
# RESET PASSWORD
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
        return {"error": "Expired"}

    if new_password != confirm_password:
        return {"error": "Mismatch"}

    admin = db.query(Admin).filter(Admin.id == data["admin_id"]).first()

    admin.username = username
    admin.hashed_password = pwd_context.hash(new_password)

    db.commit()

    del reset_tokens[token]

    return RedirectResponse("/admin/login", status_code=303)

# =========================
# HEALTH
# =========================

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/enquiry")
async def create_enquiry(
    patient_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    test_name: str = Form(None),
    message: str = Form(None),
    db: Session = Depends(get_db)
):
    if not patient_name or not phone:
        raise HTTPException(400, "Name and phone required")

    enquiry = Enquiry(
        patient_name=patient_name[:100],
        phone=phone[:20],
        email=email[:100] if email else None,
        test_name=test_name[:200] if test_name else None,
        message=message[:1000] if message else None
    )

    db.add(enquiry)
    db.commit()

    db.refresh(enquiry)

    await run_in_threadpool(
        send_whatsapp_enquiry,
        enquiry
    )

    return RedirectResponse("/", status_code=303)



@app.get("/sitemap.xml")
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.bayapathlab.com/</loc>
        <lastmod>2026-06-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""

    return Response(
        content=xml,
        media_type="application/xml"
    )


@app.get("/robots.txt")
def robots():
    txt = """User-agent: *
Allow: /

Sitemap: https://www.bayapathlab.com/sitemap.xml"""

    return Response(
        content=txt,
        media_type="text/plain"
    )
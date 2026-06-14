import bcrypt
from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from . import models
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI(middleware=[Middleware(SessionMiddleware, secret_key="super-secret")])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return RedirectResponse("/register/")

@app.get("/register/")
def get_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register/")
def register(
    email: str = Form(...), password: str = Form(...),
    first_name: str = Form(...), last_name: str = Form(...),
    gender: str = Form(...), nationality: str = Form(...),
    organization: str = Form(...), job_title: str = Form(...),
    birth_date: str = Form(...), db: Session = Depends(get_db)
):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = models.User(
        email=email, hashed_password=hashed, first_name=first_name,
        last_name=last_name, gender=gender, nationality=nationality,
        organization=organization, job_title=job_title, birth_date=birth_date
    )
    db.add(user)
    db.commit()
    return RedirectResponse("/login/", status_code=303)

@app.get("/login/")
def get_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login/")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        request.session["user_id"] = user.id
        return RedirectResponse("/dashboard/", status_code=303)
    return RedirectResponse("/login/", status_code=303)

@app.get("/dashboard/")
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse("/login/")
    users = db.query(models.User).all()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"users": users})

@app.get("/edit/{user_id}")
def get_edit_page(request: Request, user_id: int, db: Session = Depends(get_db)):
    if request.session.get("user_id") != user_id:
        raise HTTPException(status_code=403)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse(request=request, name="edit.html", context={"user": user})

@app.post("/edit/{user_id}")
def update_user(
    request: Request,
    user_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    organization: str = Form(...),
    job_title: str = Form(...),
    db: Session = Depends(get_db)
):
    if request.session.get("user_id") != user_id:
        raise HTTPException(status_code=403)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.first_name = first_name
    user.last_name = last_name
    user.organization = organization
    user.job_title = job_title
    db.commit()
    return RedirectResponse("/dashboard/", status_code=303)
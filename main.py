from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_user_id(request: Request):
    return request.cookies.get("user_id")

# --- ВХОД / РЕГИСТРАЦИЯ ---

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
    if not user:
        return RedirectResponse(url="/login?error=Некорректные данные", status_code=303)
    res = RedirectResponse(url="/", status_code=303)
    res.set_cookie(key="user_id", value=str(user.id)) 
    return res

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    new_user = models.User(username=username, password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
def logout():
    res = RedirectResponse(url="/login")
    res.delete_cookie("user_id")
    return res

# --- РАБОТА С ЖИВОТНЫМИ ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(database.get_db)):
    uid = get_user_id(request)
    if not uid: return RedirectResponse(url="/login")
    user = db.query(models.User).filter(models.User.id == int(uid)).first()
    animals = db.query(models.Animal).filter(models.Animal.owner_id == int(uid)).all()
    return templates.TemplateResponse("index.html", {"request": request, "animals": animals, "user": user})

@app.post("/animals/add")
def add_animal(request: Request, name: str = Form(...), species: str = Form(...), age: float = Form(...), db: Session = Depends(database.get_db)):
    uid = get_user_id(request)
    new_animal = models.Animal(name=name, species=species, age=age, owner_id=int(uid))
    db.add(new_animal)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/animals/edit/{animal_id}", response_class=HTMLResponse)
def edit_page(request: Request, animal_id: int, db: Session = Depends(database.get_db)):
    uid = get_user_id(request)
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id, models.Animal.owner_id == int(uid)).first()
    if not animal: return RedirectResponse("/")
    return templates.TemplateResponse("edit.html", {"request": request, "animal": animal})

@app.post("/animals/update/{animal_id}")
def update_animal(request: Request, animal_id: int, name: str = Form(...), species: str = Form(...), age: float = Form(...), db: Session = Depends(database.get_db)):
    uid = get_user_id(request)
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id, models.Animal.owner_id == int(uid)).first()
    if animal:
        animal.name, animal.species, animal.age = name, species, age
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/animals/delete/{animal_id}")
def delete_animal(request: Request, animal_id: int, db: Session = Depends(database.get_db)):
    uid = get_user_id(request)
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id, models.Animal.owner_id == int(uid)).first()
    if animal:
        db.delete(animal)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
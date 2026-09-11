from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.db import init_db, SessionLocal
from database.seed import seed_tipos
from routers import calculo, dashboard, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_tipos(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Calculadora de Series Matemáticas", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, tags=["Autenticación"])
app.include_router(calculo.router, tags=["Cálculo"])
app.include_router(dashboard.router, tags=["Dashboard"])
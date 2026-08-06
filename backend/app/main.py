from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import APP_VERSION
from app.news.router import router as news_router
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.employees.router import router as employees_router

app = FastAPI(
  title="CRM Backend API — pet project",
  version=APP_VERSION,
  description="A simplified CRM system built with FastAPI and SQLAlchemy. It provides APIs to manage customers, news, and other related data. The project is inspired by real production CRM systems I worked with at my previous company.",
)

# Allow requests from the Vite dev server (frontend runs on localhost:5173)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# Register routers
app.include_router(news_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(employees_router)

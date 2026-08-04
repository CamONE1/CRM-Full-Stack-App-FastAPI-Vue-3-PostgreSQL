from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.news.router import router as news_router
from app.auth.router import router as auth_router

app = FastAPI(
  title="CRM Backend API — pet project",
  version="0.2.0",
  description="A simplified CRM system built with FastAPI and SQLAlchemy. It provides APIs to manage customers, news, and other related data. The project is inspired by real production CRM systems I worked with at my previous company.",
)

# Разрешаем запросы с dev-сервера Vite (frontend будет на localhost:5173)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# Подключаем роутер
app.include_router(news_router)
app.include_router(auth_router)

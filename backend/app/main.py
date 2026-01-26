from fastapi import FastAPI
from app.news.router import router as news_router

app = FastAPI(
  title="CRM Backend API — pet project",
  version="0.1.0",
  description="A simplified CRM system built with FastAPI and SQLAlchemy. It provides APIs to manage customers, news, and other related data. The project is inspired by real production CRM systems I worked with at my previous company.",
)


# Подключаем роутер
app.include_router(news_router)

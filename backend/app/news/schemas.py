from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class NewsBase(BaseModel):
	title: str = Field(
		...,
		min_length=1,
		max_length=255,
		examples=["New promo launched"],
	)
	body: str = Field(
		...,
		min_length=1,
		examples=["We launched a new promo campaign for EU markets."]
	)

class NewsCreate(NewsBase):
	pass

class News(NewsBase):
	id: int
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
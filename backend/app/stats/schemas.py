from pydantic import BaseModel

from app.news.schemas import News as NewsOut
from app.offers.schemas import OfferOut, OfferStatus


class OffersStats(BaseModel):
	total: int
	by_status: dict[OfferStatus, int]


class EmployeesStats(BaseModel):
	total: int
	active: int
	inactive: int
	by_department: dict[str, int]


class StatsOut(BaseModel):
	offers: OffersStats
	employees: EmployeesStats
	recent_offers: list[OfferOut]
	recent_news: list[NewsOut]

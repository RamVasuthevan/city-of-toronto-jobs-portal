from datetime import date

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class SearchResult(SQLModel):
    """SQLModel for City of Toronto Job search portal search results"""

    job_id: str = Field(primary_key=True)
    relative_url: str
    title: str
    job_stream: str | None = None
    position_type: str
    posting_date: date
    portal: str

    @field_validator("posting_date", mode="before")
    @classmethod
    def parse_posting_date(cls, value):
        if isinstance(value, date):
            return value
        from datetime import datetime

        return datetime.strptime(value, "%b %d, %Y").date()

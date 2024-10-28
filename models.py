import json
import os
import time
from datetime import date, datetime
from time import sleep
from typing import NewType, Optional, Union

import requests
from bs4 import BeautifulSoup
from pydantic import field_serializer, field_validator
from sqlmodel import Field, SQLModel


class Job(SQLModel):
    """SQLModel for Toronto job postings"""
    job_id: str = Field(primary_key=True)
    relative_url: str
    title: str
    job_stream: Optional[str] = None
    position_type: str
    posting_date: date 
    portal: str

    @field_validator('posting_date', mode='before')
    @classmethod
    def parse_posting_date(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(value, '%b %d, %Y').date()
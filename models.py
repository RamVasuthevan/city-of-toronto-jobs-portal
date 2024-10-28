import requests
from time import sleep
import os
from datetime import datetime, date
import time
from bs4 import BeautifulSoup
import json
from typing import Optional, Union
from sqlmodel import SQLModel, Field
from pydantic import field_validator, field_serializer
from typing import NewType

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
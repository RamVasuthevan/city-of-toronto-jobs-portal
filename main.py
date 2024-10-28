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

from util import DateEncoder

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

JOB_PORTAL_SLUGS = ['jobsatcity', 'recreation']
BASE_URL_TEMPLATE = "https://jobs.toronto.ca/{portal}/tile-search-results/"
ITEMS_PER_PAGE = 25
SLEEP_BETWEEN_REQUESTS = 2
SLEEP_BETWEEN_PORTALS = SLEEP_BETWEEN_REQUESTS
END_OF_JOBS_MARKER = "<!DOCTYPE HTML>"

DOWNLOAD_DIR = 'downloaded'
SEARCH_PAGE_DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, 'search')
OUTPUT_PATH_TEMPLATE = os.path.join(SEARCH_PAGE_DOWNLOAD_DIR, '{portal}')
PARSED_JOBS_FILE = os.path.join(DOWNLOAD_DIR, 'parsed_jobs.json')

class DownloadError(Exception):
    """Raised when a page download fails"""
    pass

HTMLString = NewType('HTMLString', str)

def download_search_page(url: str, page_number: int) -> HTMLString:
    params = {
        'q': '',  # Search query
        'startrow': page_number * ITEMS_PER_PAGE,  # Pagination offset
        '_': int(time.time() * 1000),  # Cache busting timestamp
        # 'sortColumn': 'referencedate',  # Sort by reference/posting date
        # 'sortDirection': 'desc',        # Sort direction (ascending/descending)
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            return HTMLString(response.text)
        else:
            raise DownloadError(f"Expected HTML content but received '{content_type}' on page {page_number}")
    
    except requests.RequestException as e:
        raise DownloadError(f"Failed to download page {page_number}: {str(e)}")

def download_all_search_pages_for_portal(portal: str) -> list[HTMLString]:
    url = BASE_URL_TEMPLATE.format(portal=portal)
    all_pages = []
    
    page_number = 0
    while True:
        content = download_search_page(url, page_number)
        
        if not content:
            raise DownloadError(f"Failed to get content for page {page_number} for {portal}")
            
        if content.strip().lower() == END_OF_JOBS_MARKER.lower():
            print(f"Reached end of jobs at page {page_number} for {portal}")
            break
        
        all_pages.append(content)
        print(f"Downloaded {portal} page {page_number}")
        page_number += 1
        sleep(SLEEP_BETWEEN_REQUESTS)
    
    return all_pages

def write_search_pages_to_directory(pages: list[HTMLString], portal: str) -> None:
    output_dir = OUTPUT_PATH_TEMPLATE.format(portal=portal)
    os.makedirs(output_dir, exist_ok=True)
    
    for page_number, content in enumerate(pages):
        output_file = os.path.join(output_dir, f"{page_number}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

def read_search_page_from_directory(portal: str, page_number: int) -> HTMLString:
    search_dir = OUTPUT_PATH_TEMPLATE.format(portal=portal)
    file_path = os.path.join(search_dir, f"{page_number}.html")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return HTMLString(f.read())
    except FileNotFoundError:
        raise DownloadError(f"Page {page_number} not found for {portal}")

def read_all_search_pages_for_portal_from_directory(portal: str) -> list[HTMLString]:
    search_dir = OUTPUT_PATH_TEMPLATE.format(portal=portal)
    if not os.path.exists(search_dir):
        raise FileNotFoundError(f"No downloaded files found for {portal} at {search_dir}")
    
    pages = []
    page_number = 0
    
    while True:
        try:
            page = read_search_page_from_directory(portal, page_number)
            pages.append(page)
            page_number += 1
        except DownloadError:
            break
    
    return pages

def parse_jobs_from_search_page(page: HTMLString, portal: str) -> list[Job]:
    soup = BeautifulSoup(page, 'html.parser')
    jobs = []
    
    for job_tile in soup.find_all('li', class_='job-tile'):
        desktop_section = job_tile.find('div', class_='sub-section-desktop')
        if not desktop_section:
            raise ValueError(f"Could not find desktop section in job tile: {job_tile['class']}")
            
        job_stream_elem = desktop_section.find('div', id=lambda x: x and 'desktop-section-department-value' in x)
        job_stream = job_stream_elem.text.strip() if job_stream_elem else None
            
        job = Job(
            job_id=[cls for cls in job_tile['class'] if cls.startswith('job-id-')][0].replace('job-id-', ''),
            relative_url=job_tile['data-url'],
            title=desktop_section.find('a', class_='jobTitle-link').text.strip(),
            job_stream=job_stream,
            position_type=desktop_section.find('div', id=lambda x: x and 'desktop-section-shifttype-value' in x).text.strip(),
            posting_date=desktop_section.find('div', id=lambda x: x and 'desktop-section-date-value' in x).text.strip(),
            portal=portal
        )
        jobs.append(job)
    
    return jobs

def parse_all_jobs_from_portal(pages: list[HTMLString], portal: str) -> list[Job]:
    jobs = []
    
    for page_number, content in enumerate(pages):
        page_jobs = parse_jobs_from_search_page(content, portal)
        jobs.extend(page_jobs)
        print(f"Parsed {len(page_jobs)} jobs from page {page_number}")
    
    return jobs

def download_and_parse_form_all_portals():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(SEARCH_PAGE_DOWNLOAD_DIR, exist_ok=True)
    
    all_jobs = {}
    for portal in JOB_PORTAL_SLUGS:
        print(f"Starting download for {portal}")
        pages = download_all_search_pages_for_portal(portal)
        write_search_pages_to_directory(pages, portal)
        
        print(f"Parsing jobs for {portal}")
        jobs = parse_all_jobs_from_portal(pages, portal)
        jobs_dict = [job.model_dump() for job in jobs]
        all_jobs[portal] = jobs_dict
        print(f"Found {len(jobs)} jobs for {portal}")
        
        sleep(SLEEP_BETWEEN_PORTALS)
        
    with open(PARSED_JOBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=2, cls=DateEncoder)
    print(f"Saved parsed results to {PARSED_JOBS_FILE}")

if __name__ == "__main__":
    download_and_parse_form_all_portals()
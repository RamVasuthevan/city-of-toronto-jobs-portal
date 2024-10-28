import json
import os
import time
from time import sleep
from typing import NewType

import requests
from bs4 import BeautifulSoup

from models import Job
from util import CustomJSONEncoder, download_search_pages_and_parse_jobs_write_to_directory_for_all_portals

JOB_PORTAL_SLUGS = ['jobsatcity', 'recreation']
SEARCH_PAGE_URL_TEMPLATE = "https://jobs.toronto.ca/{portal}/tile-search-results/"
ITEMS_PER_SEARCH_PAGE = 25

SLEEP_BETWEEN_REQUESTS = 2
SLEEP_BETWEEN_PORTALS = SLEEP_BETWEEN_REQUESTS
END_OF_JOBS_MARKER = "<!DOCTYPE HTML>"

DOWNLOAD_DIR = 'downloaded'
SEARCH_PAGE_DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, 'search')
SEARCH_PAGE_OUTPUT_PATH_TEMPLATE = os.path.join(SEARCH_PAGE_DOWNLOAD_DIR, '{portal}')
JOB_PAGE_DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, 'job')
JOB_PAGE_OUTPUT_PATH_TEMPLATE = os.path.join(JOB_PAGE_DOWNLOAD_DIR, '{portal}')

PARSED_JOBS_FILE = os.path.join(DOWNLOAD_DIR, 'parsed_jobs.json')

JOB_PAGE_URL_TEMPLATE = "https://jobs.toronto.ca/{relative_url}"

class DownloadError(Exception):
    """Raised when a page download fails"""
    pass

HTMLString = NewType('HTMLString', str)

def download_search_page(url: str, page_number: int) -> HTMLString:
    params = {
        'q': '',  # Search query
        'startrow': page_number * ITEMS_PER_SEARCH_PAGE,  # Pagination offset
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

def download_job_page(url: str) -> HTMLString:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            raise DownloadError(f"Expected HTML content but received '{content_type}' for URL: {url}")
        
        return HTMLString(response.text)
        
    except requests.RequestException as e:
        raise DownloadError(f"Failed to download job page {url}: {str(e)}")
    
def download_search_pages_for_portal(portal: str) -> list[HTMLString]:
    url = SEARCH_PAGE_URL_TEMPLATE.format(portal=portal)
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

def download_search_pages_for_all_portals() -> dict[str, list[HTMLString]]:    
    pages_by_portal = {}
    for portal in JOB_PORTAL_SLUGS:
        print(f"Starting download for {portal}")
        pages = download_search_pages_for_portal(portal)
        pages_by_portal[portal] = pages
        sleep(SLEEP_BETWEEN_PORTALS)
    
    return pages_by_portal

def write_search_pages_for_portal_to_directory(pages: list[HTMLString], portal: str) -> None:
    output_dir = SEARCH_PAGE_OUTPUT_PATH_TEMPLATE.format(portal=portal)
    os.makedirs(output_dir, exist_ok=True)
    
    for page_number, content in enumerate(pages):
        output_file = os.path.join(output_dir, f"{page_number}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

def write_job_pages_for_portal_to_directory(pages: list[HTMLString], portal: str) -> None:
    output_dir = JOB_PAGE_OUTPUT_PATH_TEMPLATE.format(portal=portal)
    os.makedirs(output_dir, exist_ok=True)

    for page_number, content in enumerate(pages):
        output_file = os.path.join(output_dir, f"{page_number}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

def write_search_pages_for_portals_to_directory(pages_by_portal: dict[str, list[HTMLString]]) -> None:
    for portal, pages in pages_by_portal.items():
        write_search_pages_for_portal_to_directory(pages, portal)

def read_search_page_from_directory(portal: str, page_number: int) -> HTMLString:
    search_dir = SEARCH_PAGE_OUTPUT_PATH_TEMPLATE.format(portal=portal)
    file_path = os.path.join(search_dir, f"{page_number}.html")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return HTMLString(f.read())
    except FileNotFoundError:
        raise DownloadError(f"Page {page_number} not found for {portal}")

def read_search_pages_for_portal(portal: str) -> list[HTMLString]:
    search_dir = SEARCH_PAGE_OUTPUT_PATH_TEMPLATE.format(portal=portal)
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

def read_search_pages_for_all_portals_from_directory() -> dict[str, list[HTMLString]]:
    pages_by_portal = {}
    for portal in JOB_PORTAL_SLUGS:
        pages = read_search_pages_for_portal(portal)
        pages_by_portal[portal] = pages
    
    return pages_by_portal

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

def parse_jobs_from_search_pages(pages: list[HTMLString], portal: str) -> list[Job]:
    jobs = []
    
    for page_number, content in enumerate(pages):
        page_jobs = parse_jobs_from_search_page(content, portal)
        jobs.extend(page_jobs)
        print(f"Parsed {len(page_jobs)} jobs from page {page_number}")
    
    return jobs

def parse_jobs_from_search_pages_for_portals(pages_by_portal: dict[str, list[HTMLString]]) -> dict[str, list[Job]]:
    jobs_by_portal = {}
    for portal, pages in pages_by_portal.items():
        print(f"Parsing jobs for {portal}")
        jobs = parse_jobs_from_search_pages(pages, portal)
        jobs_by_portal[portal] = jobs
        print(f"Found {len(jobs)} jobs for {portal}")
    
    return jobs_by_portal


def read_jobs_from_json(filepath: str) -> dict[str, list[Job]]:
    """
    Read jobs from a JSON file and convert them to Job model instances
    """
    with open(filepath, 'r') as f:
        jobs_data = json.load(f)
    
    # Convert the jobs data to Job model instances
    jobs_by_portal = {
        portal: [Job(**job) for job in portal_jobs]
        for portal, portal_jobs in jobs_data.items()
    }
    
    return jobs_by_portal


if __name__ == "__main__":
    #jobs_by_portal = download_search_pages_and_parse_jobs_write_to_directory_for_all_portals()

    jobs_by_portal = read_jobs_from_json(os.path.join(DOWNLOAD_DIR, 'jobs_by_portal.json'))

    jobs = jobs_by_portal['jobsatcity'][:3]
    job_pages = []
    for job in jobs:
        print(job)
        url = JOB_PAGE_URL_TEMPLATE.format(relative_url=job.relative_url)
        job_pages.append(download_job_page(url))
    write_job_pages_for_portal_to_directory(job_pages, 'jobsatcity')

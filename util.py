import inspect
import json
import os
from datetime import date
from types import ModuleType
from typing import Callable, List

from models import Job


class CustomJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles Job models and dates"""
    def default(self, obj):
        if isinstance(obj, Job):
            return obj.model_dump()
        if isinstance(obj, date):
            return obj.strftime('%b %d, %Y')
        return super().default(obj)




def get_all_functions_in_module(module: ModuleType) -> List[Callable]:
    return [name for name, obj in module.__dict__.items() if inspect.isfunction(obj)]


def download_search_pages_and_parse_jobs_write_to_directory_for_all_portals() -> dict[str, list[Job]]:
    import main
    pages_by_portal = main.download_search_pages_for_all_portals()
    main.write_search_pages_for_portals_to_directory(pages_by_portal)

    pages_by_portal = main.read_search_pages_for_all_portals_from_directory()
    main.write_search_pages_for_portals_to_directory(pages_by_portal)
    jobs_by_portal = main.parse_jobs_from_search_pages_for_portals(pages_by_portal)


    with open(os.path.join(main.DOWNLOAD_DIR, 'jobs_by_portal.json'), 'w') as f:
        f.write(json.dumps(jobs_by_portal, cls=CustomJSONEncoder, indent=4))
    
    return jobs_by_portal
import json
from datetime import date

from models import Job


class CustomJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles Job models and dates"""
    def default(self, obj):
        if isinstance(obj, Job):
            return obj.model_dump()
        if isinstance(obj, date):
            return obj.strftime('%b %d, %Y')
        return super().default(obj)
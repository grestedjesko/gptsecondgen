from datetime import datetime, timedelta
from enum import Enum

async def get_week_start_date():
    return datetime.now().date() - timedelta(days=datetime.today().weekday())


async def get_new_week_start_date():
    new_week_start_date = datetime.now().date() - timedelta(days=datetime.today().weekday()) + timedelta(days=7)
    return datetime.strftime(new_week_start_date, '%d.%m.%Y 00:00')

def json_serializer(obj):
    def json_serializer(obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)  # или str(obj), если важна точность
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

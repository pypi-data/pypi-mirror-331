import uuid
from datetime import datetime

import pytz


class MiscUtils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def convert_to_datetime(date_str: str) -> datetime:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=pytz.UTC
            )
            return date_obj
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date_str}. Expected format: 'YYYY-MM-DDTHH:MM:SS.sssZ'"
            )

    @classmethod
    def format_date_in_ist(cls, date_str: str) -> str:
        try:
            # Convert input string to datetime object in UTC
            date_obj = cls.convert_to_datetime(date_str=date_str)
            # Convert to IST
            ist = pytz.timezone("Asia/Kolkata")
            date_obj_ist = date_obj.astimezone(ist)

            # Format the date as "24 Feb'25, 01:27 PM"
            formatted_date = date_obj_ist.strftime("%d %b'%y, %I:%M %p")
            return formatted_date
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date_str}. Expected format: 'YYYY-MM-DDTHH:MM:SS.sssZ'"
            )

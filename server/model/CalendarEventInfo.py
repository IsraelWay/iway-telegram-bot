from datetime import datetime
from typing import Optional, List, Dict, Any


class CalendarEventInfo():
    def __init__(
        self,
        id: str,
        date: str,
        start_time: str,
        end_time: str,
        event_name: str,
        subject: Optional[str] = None,
        speaker: Optional[str] = None,
        description: Optional[str] = None,
        map_link: Optional[str] = None,
        address: Optional[str] = None,
        tags: Optional[List[str]] = None,
        files: Optional[List[Dict[str, Any]]] = None
    ):
        self.id = id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.event_name = event_name
        self.subject = subject
        self.speaker = speaker
        self.description = description
        self.map_link = map_link
        self.address = address
        self.tags = tags or []
        self.files = files or []

    @staticmethod
    def from_record(record: dict):
        if not isinstance(record, dict):
            return None

        rid = record.get("id")
        fields = record.get("fields") or {}
        if not rid or not isinstance(fields, dict):
            return None

        # Parse date field and convert to dd.MM.YYYY format
        date_str = fields.get("fldoAhFThMUITRPDe")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date = date_obj.strftime("%d.%m.%Y")
            except (ValueError, TypeError):
                date = date_str
        else:
            date = ""

        start_time = fields.get("fldj0YbUXN327CsbH") or ""
        end_time = fields.get("fldxKsIvsOub8aQiv") or ""
        
        # Event name from formula field or Name field
        event_name = fields.get("fldZ7fbtjgCPm235e") or fields.get("Name") or ""
        
        # Return None if critical fields are missing
        if not event_name or not date:
            return None
        
        subject = None
        subject_data = fields.get("fld31JYAs3bQDKdf1")
        if isinstance(subject_data, list) and len(subject_data) > 0:
            subject = subject_data[0]
        
        speaker = None
        speaker_data = fields.get("fld26s5ItcIsXFhHb")
        if isinstance(speaker_data, list) and len(speaker_data) > 0:
            speaker = str(speaker_data[0])
        
        description = fields.get("fldG1J7zXt6lH7dnN") or ""
        map_link = fields.get("fldcwesZdoxH7CkSkURL") or ""
        address = fields.get("fldpX2lGAJLsVIBnC")
        
        tags = []
        tags_data = fields.get("fldAyvS7HCA0Rk0sr")
        if isinstance(tags_data, list):
            tags = tags_data
        elif isinstance(tags_data, str):
            tags = [tags_data]
        
        files = []
        files_data = fields.get("fldl1bRLAbitKHbSh")
        if isinstance(files_data, list):
            files = files_data

        return CalendarEventInfo(
            id=rid,
            date=date,
            start_time=start_time,
            end_time=end_time,
            event_name=event_name,
            subject=subject,
            speaker=speaker,
            description=description,
            map_link=map_link,
            address=address,
            tags=tags,
            files=files
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "event_name": self.event_name,
            "subject": self.subject,
            "speaker": self.speaker,
            "description": self.description,
            "map_link": self.map_link,
            "address": self.address,
            "tags": self.tags,
            "files": self.files
        }

from typing import List, Optional


class EventData():
    def __init__(self, id: str, name: str, teacher_name: Optional[List[str]] = None):
        self.id = id
        self.name = name
        self.teacher_name = teacher_name or []

    @staticmethod
    def from_record(record: dict):
        if not isinstance(record, dict):
            return None

        rid = record.get("id")
        fields = record.get("fields") or {}
        if not rid or not isinstance(fields, dict):
            return None
        
        name = fields.get("fldReJymRoetXn8jE")
        teacher_name = fields.get("fldjSoE7IO1vqfIMS", [])
        
        # Ensure teacher_name is a list
        if not isinstance(teacher_name, list):
            teacher_name = [teacher_name] if teacher_name else []

        return EventData(id=rid, name=name, teacher_name=teacher_name)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "teacher_name": self.teacher_name
        }

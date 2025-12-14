class ProgramInfo():
    def __init__(self, id: str, name: str, type: str, city: str):
        self.id = id
        self.name = name
        self.type = type
        self.city = city


    @staticmethod
    def from_record(record: dict):
        if not isinstance(record, dict):
            return None

        rid = record.get("id")
        fields = record.get("fields") or {}
        if not rid or not isinstance(fields, dict):
            return None
        name = fields.get("Официальное название")
        city = fields.get("Город")
        program_type = fields.get("Type")

        return ProgramInfo(id=rid, name=name, type=program_type, city=city)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "city": self.city
        }
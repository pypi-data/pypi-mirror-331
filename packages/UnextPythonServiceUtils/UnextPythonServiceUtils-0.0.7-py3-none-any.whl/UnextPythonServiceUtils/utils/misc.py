import uuid


class MiscUtils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid.uuid4())

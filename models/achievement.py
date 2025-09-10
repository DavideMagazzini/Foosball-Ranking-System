from dataclasses import dataclass
from bson import ObjectId

@dataclass
class Achievement:
    name: str
    description: str 
    criteria: dict
    badge: str
    _id: ObjectId | str = None  # Optional, set when loaded from DB

    def __post_init__(self):
       pass
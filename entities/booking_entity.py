from dataclasses import dataclass
from datetime import datetime


@dataclass
class BookingEntity:
    table_id: int
    date: datetime
    client_name: str
    client_phone: str
    id: int | None = None

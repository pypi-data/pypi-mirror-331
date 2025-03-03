import uuid

from datetime import date, time
from typing import Optional

from dataclasses import dataclass, field


@dataclass
class Match:
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_score: int = 0
    away_score: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: date = field(default_factory=lambda: date(1970, 1, 1))
    time: time = field(default_factory=lambda: time(0, 0, 0))
    penalty_shootout: bool = False

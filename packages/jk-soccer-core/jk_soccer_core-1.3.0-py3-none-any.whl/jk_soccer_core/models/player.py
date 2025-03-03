from dataclasses import dataclass

from typing import Optional


@dataclass
class Player:
    name: str
    position: Optional[str] = None
    number: int = 0

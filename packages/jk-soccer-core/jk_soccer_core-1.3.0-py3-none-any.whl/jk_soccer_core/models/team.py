import uuid

from dataclasses import dataclass, field

from jk_soccer_core.models import Player
from jk_soccer_core.models import Coach


@dataclass
class Team:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    players: list[Player] = field(default_factory=list)
    coaches: list[Coach] = field(default_factory=list)

from dataclasses import dataclass

from typing import Optional


@dataclass
class Coach:
    name: Optional[str] = None
    title: Optional[str] = None

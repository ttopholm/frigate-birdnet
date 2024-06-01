from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, RootModel


class Data(BaseModel):
    score: float
    top_score: float
    type: str


class Event(BaseModel):
    box: Any
    camera: str
    data: Data
    end_time: float
    false_positive: Any
    has_clip: bool
    has_snapshot: bool
    id: str
    label: str
    plus_id: Any
    retain_indefinitely: bool
    start_time: float
    sub_label: Any
    thumbnail: str
    top_score: Any
    zones: List
    duration: float = 0

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.duration = self.end_time - self.start_time 

class Events(RootModel):
    root: List[Event]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


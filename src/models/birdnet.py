from __future__ import annotations

from typing import List

from pydantic import BaseModel, RootModel


class Bird(BaseModel):
    common_name: str
    scientific_name: str
    start_time: float
    end_time: float
    confidence: float
    label: str


class Birds(RootModel):
    root: List[Bird]
    
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
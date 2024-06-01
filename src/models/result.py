from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Bird(BaseModel):
    image_url: Optional[str]
    common_name: str
    scientific_name: str
    start_time: float
    end_time: float
    species_code: Optional[str]
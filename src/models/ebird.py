from __future__ import annotations

from typing import List

from pydantic import BaseModel, RootModel


class Bird(BaseModel):
    sciName: str
    comName: str
    speciesCode: str
    category: str
    taxonOrder: float
    bandingCodes: List[str]
    comNameCodes: List[str]
    sciNameCodes: List[str]
    order: str
    familyCode: str
    familyComName: str
    familySciName: str
    image: str = ""


class Birds(RootModel):
    root: List[Bird]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

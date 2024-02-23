from abc import ABC
from typing import Optional
from pydantic import BaseModel


class AbstractAdvertisements(BaseModel, ABC):
    title: str
    description: str
    owner: str


class CreateAdvertisements(AbstractAdvertisements):
    title: str
    description: str
    owner: str
     

class UpdateAdvertisements(AbstractAdvertisements):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
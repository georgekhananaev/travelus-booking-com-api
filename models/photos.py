from typing import List, Optional
from pydantic import BaseModel


class Tag(BaseModel):
    id: Optional[int] = None
    tag: Optional[str] = None


class MLTag(BaseModel):
    confidence: Optional[int] = None
    tag_type: Optional[str] = None
    tag_id: Optional[int] = None
    photo_id: Optional[int] = None
    tag_name: Optional[str] = None


class Photo(BaseModel):
    descriptiontype_id: Optional[int] = None
    ml_tags: Optional[List[MLTag]] = []
    photo_id: Optional[int] = None
    tags: Optional[List[Tag]] = []
    url_square60: Optional[str] = None
    url_max: Optional[str] = None
    url_1440: Optional[str] = None

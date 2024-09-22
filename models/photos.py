from typing import List, Optional
from pydantic import BaseModel


class Tag(BaseModel):
    id: Optional[int]
    tag: Optional[str]


class MLTag(BaseModel):
    confidence: Optional[int]
    tag_type: Optional[str]
    tag_id: Optional[int]
    photo_id: Optional[int]
    tag_name: Optional[str]


class Photo(BaseModel):
    descriptiontype_id: Optional[int]
    ml_tags: Optional[List[MLTag]] = []
    photo_id: Optional[int]
    tags: Optional[List[Tag]] = []
    url_square60: Optional[str]
    url_max: Optional[str]
    url_1440: Optional[str]

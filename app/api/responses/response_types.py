from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PostsResponse(BaseModel):
    id: int
    title: str
    content: str


class ParticipantsResponse(BaseModel):
    ms_id: str = Field(None, max_length=32)
    fk_linked_study: int
    session_id: str = Field(None, max_length=16)
    avatar: Optional[bytes]
    username: str = Field(None, max_length=32)
    nb_follower: int
    credibility_score: int
    game_start_time: datetime
    game_finish_time: datetime
    linked_study: int

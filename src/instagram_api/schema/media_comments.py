from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    full_name: str
    is_private: bool
    is_verified: bool
    profile_pic_url: str


class Comment(BaseModel):
    pk: str
    text: str
    user: User
    user_id: str
    media_id: str
    created_at: int
    created_at_utc: int
    comment_like_count: int
    child_comment_count: int


class ResponseData(BaseModel):
    comment_count: int
    comments: List[Comment]
    has_more_comments: bool
    sort_order: str
    next_min_id: Optional[str] = None
    pagination_token: Optional[str] = None


class MediaCommentsResponse(BaseModel):
    data: ResponseData
    status: str
    message: str | None

    @property
    def fast(self) -> List[Comment]:
        return [x for x in self.data.comments]

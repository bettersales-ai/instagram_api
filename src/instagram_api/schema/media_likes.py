from typing import List

from pydantic import BaseModel


class LikesUser(BaseModel):
    id: str
    username: str
    full_name: str
    is_private: bool
    is_verified: bool
    profile_pic_url: str


class ResponseData(BaseModel):
    users: List[LikesUser]
    user_count: int


class MediaLikesResponse(BaseModel):
    data: ResponseData
    status: str
    message: str | None

    @property
    def fast(self) -> List[LikesUser]:
        return [x for x in self.data.users]

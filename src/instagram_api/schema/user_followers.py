from typing import List
from pydantic import BaseModel


class PageInfo(BaseModel):
    has_next_page: bool
    end_cursor: str | None


class Follower(BaseModel):
    id: str
    username: str
    full_name: str
    is_private: bool
    is_verified: bool
    profile_pic_url: str
    followed_by_viewer: bool
    requested_by_viewer: bool


class Edge(BaseModel):
    node: Follower


class EdgeFollowedBy(BaseModel):
    count: int
    page_info: PageInfo
    edges: List[Edge]


class ResponseData(BaseModel):
    edge_followed_by: EdgeFollowedBy


class UserFollowersResponse(BaseModel):
    data: ResponseData
    status: str
    message: str | None

    @property
    def fast(self) -> List[Follower]:
        return [x.node for x in self.data.edge_followed_by.edges]

from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    handle: str = Field(
        ...,
        title="Instagram Handle",
        examples=["instagram_handle"],
        description="Instagram handle to analyze",
    )
    "Instagram handle to analyze"


class FollowersAnalysis(BaseModel):
    account: "InstagramInfo" = Field(
        ...,
        title="Instagram account information",
        description="Information about the Instagram account",
    )
    interest_groups: Dict[str, List["Follower"]] = Field(
        ...,
        title="Groups of followers",
        description="Groups of followers based on their interests",
    )


class PostsResponse(BaseModel):
    posts: List["InstagramPost"]


class AccountInterests(BaseModel):
    interests: List[str]


class InstagramInfo(BaseModel):
    title: str
    handle: str
    bio: str
    is_business: bool
    followers_count: int
    following_count: int
    posts_count: int


class Follower(BaseModel):
    id: str
    username: str
    full_name: str
    profile_pic_url: str
    is_private: bool
    is_verified: bool
    followed_by_viewer: bool
    requested_by_viewer: bool


class Edge(BaseModel):
    node: Follower


class PageInfo(BaseModel):
    has_next_page: bool
    end_cursor: str


class EdgeFollowedBy(BaseModel):
    count: int
    page_info: PageInfo
    edges: List[Edge]


class Data(BaseModel):
    edge_followed_by: EdgeFollowedBy


class InstagramResponse(BaseModel):
    data: Data
    status: str
    message: Optional[str] = None


class InstagramPost(BaseModel):
    id: str
    text: str
    image_url: str
    hashtags: List[str]

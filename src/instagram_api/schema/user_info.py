from typing import List

from pydantic import BaseModel


class BioLink(BaseModel):
    url: str
    title: str


class ProfilePicUrlInfo(BaseModel):
    height: int
    width: int
    url: str


class AccountInfo(BaseModel):
    pk: str
    id: str
    fbid_v2: str

    username: str
    full_name: str
    biography: str
    category: str
    is_business: bool

    public_email: str
    public_phone_number: str
    contact_phone_number: str

    city_name: str

    bio_links: List[BioLink]

    media_count: int
    follower_count: int
    following_count: int

    profile_pic_url: str

    hd_profile_pic_url_info: ProfilePicUrlInfo
    hd_profile_pic_versions: List[ProfilePicUrlInfo]


class UserInfoResponse(BaseModel):
    status: str
    data: AccountInfo
    message: str | None

    @property
    def fast(self) -> AccountInfo:
        return self.data

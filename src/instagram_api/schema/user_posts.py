from typing import List, Literal, Optional

from pydantic import BaseModel, computed_field, Field


class User(BaseModel):
    id: str
    pk: str
    pk_id: str
    username: str
    full_name: str
    is_private: bool
    is_verified: bool
    profile_pic_url: str


class PostCaption(BaseModel):
    text: str


class PostMedia(BaseModel):
    url: str
    width: int
    height: int
    type: Literal["image", "video"]


class InstagramMedia(BaseModel):
    url: str
    width: int
    height: int


class ImageVersions2(BaseModel):
    candidates: List[InstagramMedia]


class CarouselMedia(BaseModel):
    media_type: int
    image_versions2: Optional[ImageVersions2] = None
    video_versions: Optional[List[InstagramMedia]] = None


class Post(BaseModel):
    id: str
    pk: str
    code: str
    taken_at: int
    like_count: int
    media_type: int
    comment_count: int
    reshare_count: int
    caption: PostCaption

    image_versions2: Optional[ImageVersions2] = Field(exclude=True, default=None)
    carousel_media: Optional[List[CarouselMedia]] = Field(exclude=True, default=None)
    video_versions: Optional[List[InstagramMedia]] = Field(exclude=True, default=None)

    user: User

    @computed_field
    @property
    def media(self) -> List[PostMedia]:
        all_media = []
        if self.media_type == 8 and self.carousel_media:
            for media in self.carousel_media:
                if media.media_type == 1 and media.image_versions2:
                    all_media.append(
                        PostMedia(
                            type="image",
                            url=media.image_versions2.candidates[0].url,
                            width=media.image_versions2.candidates[0].width,
                            height=media.image_versions2.candidates[0].height,
                        )
                    )
                elif media.media_type == 2 and media.video_versions:
                    all_media.append(
                        PostMedia(
                            type="video",
                            url=media.video_versions[0].url,
                            width=media.video_versions[0].width,
                            height=media.video_versions[0].height,
                        )
                    )
        elif self.media_type == 1 and self.image_versions2:
            all_media.append(
                PostMedia(
                    type="image",
                    url=self.image_versions2.candidates[0].url,
                    width=self.image_versions2.candidates[0].width,
                    height=self.image_versions2.candidates[0].height,
                )
            )
        elif self.media_type == 2 and self.video_versions:
            all_media.append(
                PostMedia(
                    type="video",
                    url=self.video_versions[0].url,
                    width=self.video_versions[0].width,
                    height=self.video_versions[0].height,
                )
            )
        return all_media


class ResponseData(BaseModel):
    user: User
    num_results: int
    items: List[Post]
    next_max_id: str | None


class UserPostsResponse(BaseModel):
    data: ResponseData
    status: str
    message: str | None

    @property
    def fast(self):
        return [x for x in self.data.items]

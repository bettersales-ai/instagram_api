import pickle
import logging
from typing import Optional, List

from redis.asyncio import Redis

from instagram_api.schema.media_likes import LikesUser
from instagram_api.schema import (
    Post,
    Comment,
    Follower,
    UserInfoResponse,
)


logger = logging.getLogger(__package__)


class CacheLayer:
    def __init__(self, redis_url: str, cache_duration: int = 3600):
        self._redis = Redis.from_url(redis_url)
        self.cache_duration = cache_duration

    async def get_account_followers(self, handle: str) -> Optional[List[Follower]]:
        key = f"followers:{handle}"
        followers = await self._redis.execute_command("LRANGE", key, 0, -1)

        if followers:
            logger.debug(f"Cache hit for followers of {handle}")
            return [pickle.loads(follower) for follower in followers]
        return None

    async def cache_account_follower(self, handle: str, follower: Follower):
        key = f"followers:{handle}"
        follower_bytes = pickle.dumps(follower)

        # Use pipeline to atomically add follower and set expiration
        async with self._redis.pipeline() as pipe:
            await pipe.execute_command("RPUSH", key, follower_bytes)
            await pipe.expire(key, self.cache_duration)
            await pipe.execute()

    async def get_account_info(self, handle: str) -> Optional[UserInfoResponse]:
        key = f"account_info:{handle}"
        info = await self._redis.get(key)

        if info:
            logger.debug(f"Cache hit for account info of {handle}")
            return pickle.loads(info)
        return None

    async def cache_account_info(self, handle: str, info: UserInfoResponse):
        key = f"account_info:{handle}"
        info_bytes = pickle.dumps(info)
        await self._redis.set(key, info_bytes, ex=self.cache_duration)

    async def get_account_posts(self, handle: str) -> Optional[List[Post]]:
        key = f"posts:{handle}"
        posts = await self._redis.execute_command("LRANGE", key, 0, -1)

        if posts:
            logger.debug(f"Cache hit for posts of {handle}")
            return [pickle.loads(post) for post in posts]
        return None

    async def cache_account_post(self, handle: str, post: Post):
        key = f"posts:{handle}"
        post_bytes = pickle.dumps(post)

        # Use pipeline to atomically add post and set expiration
        async with self._redis.pipeline() as pipe:
            await pipe.execute_command("RPUSH", key, post_bytes)
            await pipe.expire(key, self.cache_duration)
            await pipe.execute()

    async def get_media_comments(self, media_id: str) -> Optional[List[Comment]]:
        key = f"comments:{media_id}"
        comments = await self._redis.execute_command("LRANGE", key, 0, -1)

        if comments:
            logger.debug(f"Cache hit for comments of media {media_id}")
            return [pickle.loads(comment) for comment in comments]
        return None

    async def cache_media_comment(self, media_id: str, comment: Comment):
        key = f"comments:{media_id}"
        comment_bytes = pickle.dumps(comment)

        # Use pipeline to atomically add comment and set expiration
        async with self._redis.pipeline() as pipe:
            await pipe.execute_command("RPUSH", key, comment_bytes)
            await pipe.expire(key, self.cache_duration)
            await pipe.execute()

    async def get_media_likes(self, media_id: str) -> Optional[List[LikesUser]]:
        key = f"likes:{media_id}"
        likes = await self._redis.execute_command("LRANGE", key, 0, -1)

        if likes:
            logger.debug(f"Cache hit for likes of media {media_id}")
            return [pickle.loads(like) for like in likes]
        return None

    async def cache_media_like(self, media_id: str, likes: LikesUser):
        key = f"likes:{media_id}"
        likes_bytes = pickle.dumps(likes)

        # Use pipeline to atomically add likes and set expiration
        async with self._redis.pipeline() as pipe:
            await pipe.execute_command("RPUSH", key, likes_bytes)
            await pipe.expire(key, self.cache_duration)
            await pipe.execute()

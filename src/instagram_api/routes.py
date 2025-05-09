from urllib.parse import urlparse
from typing import AsyncGenerator

import aiohttp

from instagram_api.schema import (
    Post,
    Comment,
    Follower,
    LikesUser,
    UserInfoResponse,
    UserPostsResponse,
    MediaLikesResponse,
    MediaCommentsResponse,
    UserFollowersResponse,
)
from instagram_api.cache import CacheLayer


class InstagramAPI:
    def __init__(self, url: str, api_key: str, redis_url: str):
        self._url = url
        self._api_key = api_key
        self._host = urlparse(url).netloc
        self._cache = CacheLayer(redis_url)

    async def user_info(self, handle: str) -> UserInfoResponse:
        headers = {
            "x-rapidapi-host": self._host,
            "x-rapidapi-key": self._api_key,
        }
        querystring = {"username_or_id": handle}
        url = f"{self._url}/v1/user_info"

        if user_info := await self._cache.get_account_info(handle):
            print(f"Cache hit for account info of {handle}")
            return user_info

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
                params=querystring,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                json_data = await response.json()

                data = UserInfoResponse(**json_data)
                if data.status == "fail":
                    raise Exception(f"API request failed: {data.message}")
                if data.status == "ok":
                    await self._cache.cache_account_info(handle, data)
                return data

    async def user_posts(
        self, handle: str, max_pagination: int = 1
    ) -> AsyncGenerator[Post, None]:
        max_p = max_pagination
        if max_p < 1:
            raise ValueError("max_pagination must be greater than 0")
        if max_p > 10:
            raise ValueError("max_pagination must be less than 10")

        headers = {
            "x-rapidapi-host": self._host,
            "x-rapidapi-key": self._api_key,
        }
        querystring = {"username_or_id": handle}
        url = f"{self._url}/v1/user_posts"

        if posts := await self._cache.get_account_posts(handle):
            for post in posts:
                yield post
            return

        async with aiohttp.ClientSession() as session:
            while max_p > 0:
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        params=querystring,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        response.raise_for_status()
                        if response.status != 200:
                            raise Exception(
                                (
                                    f"API request failed with status code: {response.status}"
                                    f" and message: {await response.text()}"
                                )
                            )
                        json_data = await response.json()

                        data = UserPostsResponse(**json_data)
                        if data.status == "fail":
                            raise Exception(f"API request failed: {data.message}")
                        if data.data.next_max_id:
                            # type: ignore
                            querystring["max_id"] = data.data.next_max_id
                        else:
                            querystring.pop("max_id", None)

                        for post in data.fast:
                            await self._cache.cache_account_post(handle, post)
                            yield post
                        max_p -= 1
                except aiohttp.ClientError as e:
                    raise Exception(f"API request failed: {str(e)}")
                except ValueError as e:
                    raise Exception(f"Invalid response data: {str(e)}")
                except Exception as e:
                    raise Exception(f"An unexpected error occurred: {str(e)}")
                finally:
                    await session.close()

    async def user_followers(
        self,
        handle: str,
        max_pagination: int = 1,
    ) -> AsyncGenerator[Follower, None]:
        max_p = max_pagination
        if max_p < 1:
            raise ValueError("max_pagination must be greater than 0")
        if max_p > 10:
            raise ValueError("max_pagination must be less than 10")

        headers = {
            "x-rapidapi-host": self._host,
            "x-rapidapi-key": self._api_key,
        }
        querystring = {"username_or_id": handle}
        url = f"{self._url}/v1/user_followers_adv"

        if followers := await self._cache.get_account_followers(handle):
            for follower in followers:
                yield follower
            return

        async with aiohttp.ClientSession() as session:
            while max_p > 0:
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        params=querystring,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        response.raise_for_status()
                        if response.status != 200:
                            raise Exception(
                                (
                                    f"API request failed with status code: {response.status}"
                                    f" and message: {await response.text()}"
                                )
                            )
                        json_data = await response.json()

                        data = UserFollowersResponse(**json_data)
                        if data.status == "fail":
                            raise Exception(f"API request failed: {data.message}")
                        if data.data.edge_followed_by.page_info.has_next_page:
                            pagination_token = (
                                data.data.edge_followed_by.page_info.end_cursor
                            )
                            # type: ignore
                            querystring["end_cursor"] = pagination_token  # type: ignore
                        else:
                            querystring.pop("end_cursor", None)

                        for follower in data.fast:
                            await self._cache.cache_account_follower(handle, follower)
                            yield follower
                        max_pagination -= 1

                except aiohttp.ClientError as e:
                    raise Exception(f"API request failed: {str(e)}")
                except ValueError as e:
                    raise Exception(f"Invalid response data: {str(e)}")
                except Exception as e:
                    raise Exception(f"An unexpected error occurred: {str(e)}")
                finally:
                    await session.close()

    async def media_comments(
        self,
        media_id: str,
        max_pagination: int = 1,
    ) -> AsyncGenerator[Comment, None]:
        max_p = max_pagination

        if max_p < 1:
            raise ValueError("max_pagination must be greater than 0")
        if max_p > 10:
            raise ValueError("max_pagination must be less than 10")
        headers = {
            "x-rapidapi-host": self._host,
            "x-rapidapi-key": self._api_key,
        }
        querystring = {
            "sort_order": "popular",
            "code_or_id_or_url": media_id,
        }

        url = f"{self._url}/v1/media_comments"
        if comments := await self._cache.get_media_comments(media_id):
            for comment in comments:
                yield comment
            return
        async with aiohttp.ClientSession() as session:
            while max_p > 0:
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        params=querystring,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        response.raise_for_status()
                        if response.status != 200:
                            raise Exception(
                                (
                                    f"API request failed with status code: {response.status}"
                                    f" and message: {await response.text()}"
                                )
                            )
                        json_data = await response.json()

                        data = MediaCommentsResponse(**json_data)
                        if data.status == "fail":
                            raise Exception(f"API request failed: {data.message}")
                        if data.data.next_min_id:
                            # type: ignore
                            querystring["min_id"] = data.data.next_min_id
                        else:
                            querystring.pop("min_id", None)

                        for comment in data.fast:
                            await self._cache.cache_media_comment(media_id, comment)
                            yield comment
                        max_p -= 1
                except aiohttp.ClientError as e:
                    raise Exception(f"API request failed: {str(e)}")
                except ValueError as e:
                    raise Exception(f"Invalid response data: {str(e)}")
                except Exception as e:
                    raise Exception(f"An unexpected error occurred: {str(e)}")
                finally:
                    await session.close()

    async def media_likes(
        self,
        media_id: str,
        max_pagination: int = 1,
    ) -> AsyncGenerator[LikesUser, None]:
        max_p = max_pagination

        if max_p < 1:
            raise ValueError("max_pagination must be greater than 0")
        if max_p > 10:
            raise ValueError("max_pagination must be less than 10")
        headers = {
            "x-rapidapi-host": self._host,
            "x-rapidapi-key": self._api_key,
        }
        querystring = {
            "sort_order": "popular",
            "code_or_id_or_url": media_id,
        }

        url = f"{self._url}/v1/media_likes"
        if likes := await self._cache.get_media_likes(media_id):
            for like in likes:
                yield like
            return
        async with aiohttp.ClientSession() as session:
            while max_p > 0:
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        params=querystring,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        response.raise_for_status()
                        if response.status != 200:
                            raise Exception(
                                (
                                    f"API request failed with status code: {response.status}"
                                    f" and message: {await response.text()}"
                                )
                            )
                        json_data = await response.json()

                        data = MediaLikesResponse(**json_data)
                        if data.status == "fail":
                            raise Exception(f"API request failed: {data.message}")

                        for like in data.fast:
                            await self._cache.cache_media_like(media_id, like)
                            yield like
                        max_p -= 1
                except aiohttp.ClientError as e:
                    raise Exception(f"API request failed: {str(e)}")
                except ValueError as e:
                    raise Exception(f"Invalid response data: {str(e)}")
                except Exception as e:
                    raise Exception(f"An unexpected error occurred: {str(e)}")
                finally:
                    await session.close()

import aiohttp
import logging

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, session=None):
        self.session = session or aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def get(self, url, params=None, headers=None):
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None
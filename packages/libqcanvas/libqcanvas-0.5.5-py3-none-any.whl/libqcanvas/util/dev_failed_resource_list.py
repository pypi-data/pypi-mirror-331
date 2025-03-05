import asyncio
import logging
from typing import Union

from aiofile import async_open
from libqcanvas_clients.util import enable_api_caching
from pydantic import RootModel

_logger = logging.getLogger(__name__)


class _NOPFailList:
    async def did_extraction_fail(self, id: str) -> bool:
        return False

    async def record_failure(self, id: str):
        pass


_FailModel = RootModel[set[str]]

_FAIL_FILE_NAME = "debug_failed_resources.json"


class FailedResourcesList:
    """
    Meant to be used as a development convenience only:
    Remembers if a resource couldn't be retrieved, so we don't bother getting it again. This is saved to disk.
    Should NOT be used for release builds!
    """

    @staticmethod
    def create_if_enabled() -> Union["FailedResourcesList", _NOPFailList]:
        if enable_api_caching:
            _logger.warning(
                'Using development "fail-db". You should not see this message in a production environment!'
            )
            return FailedResourcesList()
        else:
            return _NOPFailList()

    def __init__(self):
        self.sem = asyncio.BoundedSemaphore()
        self._loaded = False
        self._failed_ids: set | None = None

    async def _load(self):
        if self._failed_ids is None:
            async with async_open(_FAIL_FILE_NAME, "r") as file:
                self._failed_ids = _FailModel.model_validate_json(await file.read())

    async def did_extraction_fail(self, id: str) -> bool:
        async with self.sem:
            await self._load()
            return id in self._failed_ids

    async def record_failure(self, id: str):
        async with self.sem:
            self._failed_ids.add(id)

            async with async_open(_FAIL_FILE_NAME, "w") as file:
                await file.write(
                    _FailModel.model_dump_json(_FailModel(self._failed_ids))
                )

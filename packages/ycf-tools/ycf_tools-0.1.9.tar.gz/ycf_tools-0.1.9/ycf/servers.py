import asyncio
import logging
from typing import Any

import pydantic

from ycf.exceptions import MultiBaseException
from ycf.types import AliceSkillRequest, Context, HttpRequest, HttpResponse, MessagesQueueRequest

logger = logging.getLogger('ycf')


class YcfServer(object):
    _inited: bool
    _inited_lock: asyncio.Lock

    def __init__(self) -> None:
        self._inited = False
        self._inited_lock = asyncio.Lock()

    async def init(self) -> None:
        pass

    async def parsing(
        self,
        event: dict[str, Any],
        context: object,
    ) -> tuple[Context, HttpRequest | AliceSkillRequest | MessagesQueueRequest]:
        if isinstance(context, dict):
            context_obj = Context.model_validate(context)

        else:
            context_obj = Context.model_validate(context.__dict__)

        validation_exs: list[BaseException] = []

        try:
            return context_obj, HttpRequest.model_validate(event)

        except pydantic.ValidationError as ex:
            validation_exs.append(ex)

        try:
            return context_obj, AliceSkillRequest.model_validate(event)

        except pydantic.ValidationError as ex:
            validation_exs.append(ex)

        try:
            return context_obj, MessagesQueueRequest.model_validate(event)

        except pydantic.ValidationError as ex:
            validation_exs.append(ex)

        raise MultiBaseException('We were unable to parse event data', validation_exs)

    async def http_request_processing(self, context: Context, request: HttpRequest) -> dict[str, Any]:
        response = await self.http_request_handler(context, request)

        if response is None:
            return HttpResponse(200, body='None').model_dump(by_alias=True)

        if isinstance(response, HttpResponse):
            return response.model_dump(by_alias=True)

        if isinstance(response, dict):
            return HttpResponse(200, data=response).model_dump(by_alias=True)

        return HttpResponse(200, body=str(response)).model_dump(by_alias=True)

    async def alice_skill_processing(self, context: Context, request: AliceSkillRequest) -> Any:
        # This method does not imply an answer.
        await self.alice_skill_handler(context, request)
        return None

    async def queue_messages_processing(self, context: Context, request: MessagesQueueRequest) -> Any:
        # This method does not imply an answer.
        await self.queue_messages_handler(context, request)
        return None

    async def processing(
        self,
        context_object: Context,
        request_object: HttpRequest | AliceSkillRequest | MessagesQueueRequest,
    ) -> Any | None:
        if isinstance(request_object, HttpRequest):
            logger.info('Handled data for http_request_handler. Executing')
            return await self.http_request_processing(context_object, request_object)

        if isinstance(request_object, AliceSkillRequest):
            logger.info('Handled data for alice_skill_handler. Executing')
            return await self.alice_skill_processing(context_object, request_object)

        # if isinstance(request_object, MessagesQueueRequest):
        logger.info('Handled data for queue_messages_handler. Executing')
        return await self.queue_messages_processing(context_object, request_object)

    async def call(self, event: dict[str, Any], context: object) -> Any:
        async with self._inited_lock:
            if not self._inited:
                await self.init()
                self._inited = True

        context_object, request_object = await self.parsing(event, context)
        return await self.processing(context_object, request_object)

    async def __call__(self, event: dict[str, Any], context: object) -> Any:
        return await self.call(event, context)

    async def http_request_handler(
        self,
        context: Context,
        request: HttpRequest,
    ) -> str | dict[str, Any] | None:
        logger.error(f'An unexpected HttpRequest was received: {request}')
        return None

    async def alice_skill_handler(
        self,
        context: Context,
        request: AliceSkillRequest,
    ) -> str | dict[str, Any] | None:
        logger.error(f'An unexpected AliceSkillRequest was received: {request}')
        return None

    async def queue_messages_handler(
        self,
        context: Context,
        request: MessagesQueueRequest,
    ) -> str | dict[str, Any] | None:
        logger.error(f'An unexpected MessagesQueueRequest was received: {request}')
        return None

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Context(BaseModel):
    class TokenContext(BaseModel):
        access_token: str
        expires_in: int
        token_type: str

    token: TokenContext
    aws_request_id: str
    deadline_ms: int
    function_name: str
    function_version: str
    invoked_function_arn: str
    log_group_name: str
    log_stream_name: str
    memory_limit_in_mb: int
    request_id: str


class HttpRequest(BaseModel):
    class Context(BaseModel):
        class Identity(BaseModel):
            source_ip: str = Field(alias='sourceIp')
            user_agent: str = Field(alias='userAgent')

        identity: Identity
        http_method: str = Field(alias='httpMethod')
        request_id: str = Field(alias='requestId')
        request_time: str = Field(alias='requestTime')
        request_time_epoch: int = Field(alias='requestTimeEpoch')

    request_context: Context = Field(alias='requestContext')

    multi_value_headers: dict[str, list[str]] = Field(
        default_factory=dict,
        alias='multiValueHeaders',
    )
    query_string_parameters: dict[str, str] = Field(
        default_factory=dict,
        alias='queryStringParameters',
    )
    multi_value_query_string_parameters: dict[str, list[str]] = Field(
        default_factory=dict,
        alias='multiValueQueryStringParameters',
    )
    is_base64_encoded: bool = Field(alias='isBase64Encoded')

    path: str = ''
    http_method: str = Field(alias='httpMethod')
    body: str | None | dict[str, Any] = None
    headers: dict[str, str]

    @property
    def data(self) -> dict[str, Any] | list[Any] | str | Any | None:
        if self.body is None:
            return None

        if self.body == '':
            return None

        if isinstance(self.body, str):
            return json.loads(self.body)

        return self.body


class AliceSkillRequest(BaseModel):
    class MetaModel(BaseModel):
        class InterfacesModel(BaseModel):
            account_linking: dict[str, str] = {}
            payments: dict[str, str] = {}
            screen: dict[str, str] = {}

        interfaces: InterfacesModel
        client_id: str
        locale: str
        timezone: str

    class RequestModel(BaseModel):
        class MarkupModel(BaseModel):
            dangerous_context: bool

        class NluModel(BaseModel):
            entities: list[dict[str, str]]
            tokens: list[str]
            intents: dict[str, str]

        nlu: NluModel
        markup: MarkupModel
        original_utterance: str
        command: str
        type: str

    class SessionModel(BaseModel):
        class UserModel(BaseModel):
            user_id: str

        class ApplicationModel(BaseModel):
            application_id: str

        user: UserModel
        application: ApplicationModel
        message_id: int
        new: bool
        session_id: str
        skill_id: str
        user_id: str

    class StateModel(BaseModel):
        session: dict[str, str]
        user: dict[str, str]
        application: dict[str, str]

    meta: MetaModel
    request: RequestModel
    session: SessionModel
    state: StateModel
    version: str


class MessagesQueueRequest(BaseModel):
    class MessageEvent(BaseModel):
        class Details(BaseModel):
            class Message(BaseModel):
                class MessageAttribute(BaseModel):
                    class MessageAttributes(BaseModel):
                        data_type: str = Field(alias='dataType')
                        string_value: str = Field(alias='stringValue')

                    message_attribute_key: MessageAttributes = Field(alias='messageAttributeKey')

                message_id: UUID
                md5_of_body: str
                body: str
                attributes: dict[str, str]
                message_attributes: MessageAttribute
                md5_of_message_attributes: str

            message: Message
            queue_id: str

        class EventMetadata(BaseModel):
            event_id: UUID
            event_type: str
            created_at: datetime

        event_metadata: EventMetadata
        details: Details

    messages: list[MessageEvent]


class HttpResponse(BaseModel):
    status_code: int = Field(200, alias='statusCode')
    headers: dict[str, str] = Field(default_factory=dict)
    multi_value_headers: dict[str, list[str]] = Field(default_factory=dict, alias='multiValueHeaders')
    body: str
    is_base64_encoded: bool = Field(False, alias='isBase64Encoded')

    def __init__(
        self,
        status_code: int = 200,
        data: Any = None,
        body: str | None = None,
        headers: dict[str, str] | None = None,
        multi_value_headers: dict[str, list[str]] | None = None,
        is_base64_encoded: bool = False,
    ) -> None:
        assert any([body is not None, data is not None]), 'must be passed: "body" or "data"'
        assert not all([body is not None, data is not None]), 'only one variable must be passed: "body" or "data"'

        if data is not None:
            body = json.dumps(data)

        headers = {} if headers is None else headers
        multi_value_headers = {} if multi_value_headers is None else multi_value_headers

        super().__init__(
            status_code=status_code,
            body=body,
            headers=headers,
            multi_value_headers=multi_value_headers,
            is_base64_encoded=is_base64_encoded,
        )

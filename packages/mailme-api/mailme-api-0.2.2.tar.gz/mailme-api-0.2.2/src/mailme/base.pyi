from typing import NotRequired, Sequence, TypedDict
from appier import API as BaseAPI

BASE_URL: str = ...

class Ping(TypedDict):
    time: float

class Attachment(TypedDict):
    name: str
    data: str
    mime: str
    hash: str
    etag: str
    guid: str
    engine: str

class AttachmentPayload(TypedDict):
    name: str
    data: str
    mime: NotRequired[str]
    hash: NotRequired[str]
    etag: NotRequired[str]
    guid: NotRequired[str]
    engine: NotRequired[str]

class Message(TypedDict):
    sender: str | None
    receivers: Sequence[str]
    cc: Sequence[str]
    bcc: Sequence[str]
    reply_to: Sequence[str]
    subject: str
    title: str
    subtitle: str | None
    contents: str
    html: str
    plain: str
    copyright: str
    logo_url: str | None
    attachments: Sequence[Attachment]
    id: str | None
    inline: bool
    style: str
    style_css: str
    mode: str

class MessagePayload(TypedDict):
    sender: NotRequired[str]
    receivers: Sequence[str]
    subject: NotRequired[str]
    title: NotRequired[str]
    contents: NotRequired[str]
    html: NotRequired[str]
    plain: NotRequired[str]
    copyright: NotRequired[str]
    attachments: NotRequired[Sequence[AttachmentPayload]]
    inline: NotRequired[bool]
    style: NotRequired[str]
    style_css: NotRequired[str]
    mode: NotRequired[str]

class API(BaseAPI):
    def ping(self) -> Ping: ...
    def send(self, payload: MessagePayload) -> Message: ...

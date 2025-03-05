import abc
from typing import Any, AsyncIterator, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, SerializeAsAny

E = TypeVar("E")
DynamicAnalyticsOptionsMessageFormat = Literal["SELECT", "MULTI_SELECT", "CONFIRM"]
DynamicAnalyticsMessageFormat = (
    Literal["TEXT", "TABLE"] | DynamicAnalyticsOptionsMessageFormat
)


class DynamicAnalyticsMessage(BaseModel, Generic[E], extra="allow"):
    """A message to be sent to or received from the dynamic analytics service."""

    is_input: bool
    placeholder: str = ""
    format: DynamicAnalyticsMessageFormat

    body: list[E] = Field(default_factory=list)

    def to_response(self, body: list[E] | None = None) -> "DynamicAnalyticsResponse[E]":
        if body is None:
            message = self
        else:
            message = self.model_copy(update={"body": body})
        return ModelDynamicAnalyticsResponse(message)


class DynamicAnalyticsTableColumnDefinition(BaseModel):

    name: str
    type: str


class DynamicAnalyticsTableSchema(BaseModel):

    columns: list[DynamicAnalyticsTableColumnDefinition]


class DynamicAnalyticsTableMessage(DynamicAnalyticsMessage[dict[str, Any]]):

    format: DynamicAnalyticsMessageFormat = "TABLE"
    table_schema: DynamicAnalyticsTableSchema


class DynamicAnalyticsOptionsMessage(DynamicAnalyticsMessage[E], Generic[E]):

    format: DynamicAnalyticsOptionsMessageFormat
    options: list[str]


class DynamicAnalyticsResponse(abc.ABC, Generic[E]):

    @abc.abstractmethod
    def message(self) -> DynamicAnalyticsMessage[E]: ...

    @abc.abstractmethod
    async def iterator(self) -> AsyncIterator[E]:
        if False:
            yield

    @abc.abstractmethod
    def is_drained(self) -> bool: ...


class ModelDynamicAnalyticsResponse(DynamicAnalyticsResponse[E], Generic[E]):

    def __init__(self, message: DynamicAnalyticsMessage[E]) -> None:
        self._message = message

    def message(self) -> DynamicAnalyticsMessage[E]:
        return self._message

    async def iterator(self) -> AsyncIterator[E]:
        for item in self._message.body:
            yield item

    def is_drained(self) -> bool:
        return True


class BaseDynamicAnalyticsResponse(DynamicAnalyticsResponse[E], Generic[E]):

    def __init__(self, message: DynamicAnalyticsMessage[E]) -> None:
        self._message = message
        self._drained = False
        self._rows: list[E] = []

    def message(self) -> DynamicAnalyticsMessage[E]:
        if self._drained:
            return self._message.model_copy(update=dict(body=self._rows))
        return self._message

    async def iterator(self) -> AsyncIterator[E]:
        if self._drained:
            for item in self._rows:
                yield item
        else:
            async for item in self._iterator():
                self._rows.append(item)
                yield item
            self._drained = True

    @abc.abstractmethod
    async def _iterator(self) -> AsyncIterator[E]:
        if False:
            yield

    def is_drained(self) -> bool:
        return self._drained


class DynamicAnalyticsSession(abc.ABC):

    @abc.abstractmethod
    def get_initial_input(self) -> DynamicAnalyticsMessage[Any]: ...

    @abc.abstractmethod
    async def submit(
        self, input: DynamicAnalyticsMessage[Any]
    ) -> AsyncIterator[DynamicAnalyticsResponse[Any]]:
        if False:
            yield


class DynamicAnalyticsService(abc.ABC):

    @abc.abstractmethod
    async def new_session(self) -> DynamicAnalyticsSession: ...


class DynamicAnalyticsSessionModel(BaseModel):

    initial_input: DynamicAnalyticsMessage
    items: list[SerializeAsAny[DynamicAnalyticsMessage]]


class DynamicAnalyticsSessionRecorder(DynamicAnalyticsSession):

    def __init__(self, delegate: DynamicAnalyticsSession) -> None:
        self._delegate = delegate

        self._items: list[
            DynamicAnalyticsMessage[Any] | DynamicAnalyticsResponse[Any]
        ] = []

    def get_initial_input(self) -> DynamicAnalyticsMessage[Any]:
        return self._delegate.get_initial_input()

    async def submit(
        self, input: DynamicAnalyticsMessage[Any]
    ) -> AsyncIterator[DynamicAnalyticsResponse[Any]]:
        self._items.append(input)
        async for response in self._delegate.submit(input):
            if not response.message().is_input:
                self._items.append(response)
            yield response

    def serialize(self) -> DynamicAnalyticsSessionModel:
        return DynamicAnalyticsSessionModel(
            initial_input=self.get_initial_input(),
            items=[
                e.message() if isinstance(e, DynamicAnalyticsResponse) else e
                for e in self._items
            ],
        )

import typing


__all__ = ['SignParams', 'Weight', 'Event', 'AccountBalance', 'BlockHash']


class SignParams(typing.TypedDict):
    era: typing.Optional[dict]
    nonce: typing.Optional[int]


class Weight(typing.TypedDict):
    proof_size: int
    ref_time: int


class NestedEvent(typing.TypedDict):
    event_index: str
    module_id: str
    event_id: str
    attributes: dict | list | None


class Event(typing.TypedDict):
    phase: typing.Literal['ApplyExtrinsic']
    extrinsic_idx: int
    event: NestedEvent
    event_index: int
    module_id: str
    event_id: str
    attributes: dict | list | None
    topics: list


class AccountBalance(typing.NamedTuple):
    free: int
    reserved: int = 0
    frozen: int = 0

    @property
    def total(self):
        return self.free + self.reserved


BlockHash = typing.Optional[str]

import typing


__all__ = [
    'TokenPropertyPermission', 'Property', 'CrossAccountId', 'CreateCollectionParams', 'CollectionInfo', 'TokenInfo',
    'CreateTokenParams'
]


class CollectionLimits(typing.TypedDict):
    account_token_ownership_limit: typing.Optional[int]
    sponsored_data_size: typing.Optional[int]
    sponsored_data_rate_limit: typing.Optional[typing.Literal['SponsoringDisabled'] | int]
    token_limit: typing.Optional[int]
    sponsor_transfer_timeout: typing.Optional[int]
    sponsor_approve_timeout: typing.Optional[int]
    owner_can_transfer: typing.Optional[bool]
    owner_can_destroy: typing.Optional[bool]
    transfers_enabled: typing.Optional[bool]


class NestingPermissions(typing.TypedDict):
    token_owner: bool
    collection_admin: bool
    restricted: typing.Optional[list[int]]


class TokenPropertyPermissionPermission(typing.TypedDict):
    mutable: bool
    collection_admin: bool
    token_owner: bool


class TokenPropertyPermission(typing.TypedDict):
    key: str
    permission: TokenPropertyPermissionPermission


class CollectionPermissions(typing.TypedDict):
    access: typing.Optional[typing.Literal['Normal'] | typing.Literal['AllowList']]
    mint_mode: typing.Optional[bool]
    nesting: typing.Optional[NestingPermissions]


class Property(typing.TypedDict):
    key: str
    value: str


class CrossAccountId(typing.TypedDict):
    Substrate: typing.NotRequired[str]
    Ethereum: typing.NotRequired[str]


class CollectionFlags(typing.TypedDict):
    erc721metadata: bool
    foreign: bool


class CollectionInfo(typing.TypedDict):
    owner: str
    mode: typing.Literal['NFT'] | typing.Literal['RFT'] | typing.Literal['Fungible']
    name: str
    description: str
    token_prefix: str
    sponsorship: typing.Literal['Disabled'] | CrossAccountId
    limits: CollectionLimits
    permissions: CollectionPermissions
    token_property_permissions: list[TokenPropertyPermission]
    properties: list[Property]
    read_only: bool
    flags: CollectionFlags


class CreateCollectionParams(typing.TypedDict):
    access: typing.NotRequired[typing.Literal['Normal'] | typing.Literal['AllowList'] | None]
    name: str
    description: str
    token_prefix: str
    limits: typing.NotRequired[CollectionLimits | None]
    permissions: typing.NotRequired[CollectionPermissions | None]
    token_property_permissions: typing.NotRequired[list[TokenPropertyPermission] | None]
    properties: typing.NotRequired[list[Property] | None]
    admin_list: typing.NotRequired[list[CrossAccountId] | None]
    pending_sponsor: typing.NotRequired[CrossAccountId | None]
    flags: typing.NotRequired[int | None]


class TokenInfo(typing.TypedDict):
    owner: CrossAccountId
    properties: list[Property]
    pieces: int


class CreateTokenParams(typing.TypedDict):
    properties: list[Property] | None
    owner: CrossAccountId

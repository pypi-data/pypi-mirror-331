import typing

import scalecodec
import substrateinterface
from substrateinterface.utils.ss58 import ss58_encode, ss58_decode

from unique_playgrounds import types_unique, types_system


__all__ = ['UniqueHelper']


def str2vec(string):
    if not isinstance(string, str):
        return string
    return [ord(x) for x in string]


def vec2str(vec: list[int]):
    return ''.join(chr(x) for x in vec)


class LogEntry(typing.TypedDict):
    signer: str
    tx: str
    params: typing.Optional[dict]
    is_success: bool
    is_finalized: bool
    block_hash: typing.Optional[str]
    block_number: typing.Optional[int]
    extrinsic_idx: int
    extrinsic_hash: str
    fee: int
    weight: types_system.Weight
    events: list[types_system.Event]


class HelperException(Exception):
    pass


class SubstrateException(HelperException):
    pass


class UniqueHelper(object):
    def __init__(self, ws_endpoint: str = None, wait_for_finalization=True):
        self._api = None
        self.logs: list[LogEntry] = []
        self._wait_finalization = wait_for_finalization
        self._ws_endpoint = ws_endpoint
        self.address = AddressGroup(self)
        self.balance = BalanceGroup(self)
        self.chain = ChainGroup(self)
        self.nft = NFTGroup(self)

    @property
    def api(self) -> substrateinterface.SubstrateInterface:
        if self._api is None:
            raise ValueError('Helper disconnected')
        return self._api

    def connect(self, ws_endpoint: str):
        self._api = substrateinterface.SubstrateInterface(ws_endpoint)

    def disconnect(self):
        if self._api is not None:
            self._api.close()
        self._api = None

    def __enter__(self):
        self.connect(self._ws_endpoint)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def call_query(self, module, method, params=None, at=None):
        return self.api.query(module, method, params=params, block_hash=at)

    def construct_extrinsic(self, tx: str, params: dict, at: types_system.BlockHash = None) -> scalecodec.GenericCall:
        module, function = tx.split('.')
        return self.api.compose_call(
            module, function, call_params=params, block_hash=self.api.block_hash if at is None else at
        )

    def send_signed_extrinsic(
        self, signer: substrateinterface.Keypair, extrinsic: scalecodec.GenericCall,
        sign_params: typing.Optional[types_system.SignParams] = None
    ):
        signed = self.api.create_signed_extrinsic(extrinsic, signer, **(sign_params or {}))
        return self.api.submit_extrinsic(signed, wait_for_inclusion=True, wait_for_finalization=self._wait_finalization)

    def execute_extrinsic(
        self, signer: substrateinterface.Keypair, tx: str, params: dict, at: types_system.BlockHash = None,
        sign_params: typing.Optional[types_system.SignParams] = None
    ) -> LogEntry:
        extrinsic = self.construct_extrinsic(tx, params, at)
        result = self.send_signed_extrinsic(signer, extrinsic, sign_params)
        log = {
            'tx': tx,
            'params': params,
            'is_success': result.is_success,
            'is_finalized': result.finalized,
            'block_hash': result.block_hash,
            'block_number': result.block_number,
            'extrinsic_idx': result.extrinsic_idx,
            'extrinsic_hash': result.extrinsic_hash,
            'signer': signer.ss58_address,
            'fee': result.total_fee_amount,
            'weight': result.weight,
            'events': [x.value for x in result.triggered_events]
        }
        self.logs.append(log)
        error = self.find_event('System.ExtrinsicFailed', log['events'])
        if error:
            module = error['attributes']['dispatch_error']['Module']
            pallet_errors = None
            for pallet in self.api.metadata.pallets:
                if pallet.value['index'] != module['index']:
                    continue
                pallet_errors = pallet.errors
                break
            error_code = int.from_bytes(bytes.fromhex(module['error'][2:]), "little")
            error = {'name': 'SubstrateError', 'docs': [f'Unknown error (Not from metadata): {module}']}
            for e in (pallet_errors.value if pallet_errors else []):
                if e['index'] == error_code:
                    error = e
                    break
            raise SubstrateException(f'{error["name"]}: {", ".join(error["docs"])}')
        return log

    @classmethod
    def find_event(
        cls, event: str, events: list[types_system.Event],
        attributes_func: typing.Callable[[list | dict | None], bool] = lambda x: True
    ) -> types_system.Event | None:
        module_id, event_id = event.split('.')
        for e in events:
            if not (e['module_id'] == module_id and e['event_id'] == event_id):
                continue
            if attributes_func(e['attributes']):
                return e
        return None


class HelperGroup(object):
    def __init__(self, helper: UniqueHelper):
        self.helper = helper


class AddressGroup(HelperGroup):
    @classmethod
    def get_keypair(cls, seed: str) -> substrateinterface.Keypair:
        return substrateinterface.Keypair.create_from_uri(seed)

    @classmethod
    def normalize(cls, address: str, ss58_format=42) -> str:
        return ss58_encode(ss58_decode(address), ss58_format=ss58_format)


class BalanceGroup(HelperGroup):
    def get_substrate(self, address: str) -> types_system.AccountBalance:
        result = self.helper.call_query('System', 'Account', [address])
        return types_system.AccountBalance(
            free=result.value['data']['free'], reserved=result.value['data']['reserved'],
            frozen=result.value['data']['frozen']
        )

    def get_one_token(self) -> int:
        return 10 ** self.helper.chain.get_properties().token_decimals

    def transfer(self, signer: substrateinterface.Keypair, address: str, value: int, in_tokens=False) -> bool:
        if in_tokens:
            value = value * self.helper.balance.get_one_token()
        receipt = self.helper.execute_extrinsic(signer, 'Balances.transfer_keep_alive', {
            'dest': address, 'value': value
        })

        return receipt['is_success'] and self.helper.find_event(
            'Balances.Transfer', receipt['events'],
            lambda x: (
                x['amount'] == value and
                self.helper.address.normalize(x['from']) == self.helper.address.normalize(signer.ss58_address) and
                self.helper.address.normalize(x['to']) == self.helper.address.normalize(address)
            )
        ) is not None


class ChainGroup(HelperGroup):
    class ChainProperties(typing.NamedTuple):
        ss58_format: int
        token_decimals: int
        token_symbol: str

    def get_properties(self) -> ChainProperties:
        properties = self.helper.api.properties

        return self.ChainProperties(
            ss58_format=properties['ss58Format'],
            token_decimals=properties['tokenDecimals'],
            token_symbol=properties['tokenSymbol']
        )


class NFTGroup(HelperGroup):
    def get_collection_info(self, collection_id: int) -> types_unique.CollectionInfo:
        response = self.helper.api.rpc_request('unique_collectionById', [collection_id])
        result = response['result']
        if result is None:
            return None
        result.update({
            'name': vec2str(result['name']),
            'description': vec2str(result['description']),
            'token_prefix': vec2str(result['token_prefix'])
        })
        result['token_property_permissions'] = [
            {**x, 'key': vec2str(x['key'])} for x in result['token_property_permissions']
        ]
        result['properties'] = [{'key': vec2str(x['key']), 'value': vec2str(x['value'])} for x in result['properties']]
        result['owner'] = self.helper.address.normalize(result['owner'])
        return result

    def get_token_info(
        self, collection_id: int, token_id: int, property_keys: list[str] | None = None
    ) -> types_unique.TokenInfo | None:
        params = [collection_id, token_id]
        if property_keys is not None:
            params.append(property_keys)
        response = self.helper.api.rpc_request('unique_tokenData', params)
        result = response['result']
        if result['owner'] is None:
            return None
        if result['owner'].get('substrate'):
            result['owner'] = {'Substrate': self.helper.address.normalize(result['owner']['substrate'])}
        else:
            result['owner'] = {'Ethereum': result['owner']['ethereum']}
        result['properties'] = [{'key': vec2str(x['key']), 'value': vec2str(x['value'])} for x in result['properties']]
        return result

    def create_collection_simple(
        self, signer: substrateinterface.Keypair, name: str, description: str, token_prefix: str
    ) -> 'NFTCollection':
        receipt = self.helper.execute_extrinsic(signer, 'Unique.create_collection', {
            'collection_name': [str2vec(name)],
            'collection_description': [str2vec(description)],
            'token_prefix': token_prefix, 'mode': {'NFT': None}
        })
        event = self.helper.find_event('Common.CollectionCreated', receipt['events'])
        collection_id, collection_type, owner = event['attributes']

        return NFTCollection(self.helper, collection_id)

    def create_collection(
        self, signer: substrateinterface.Keypair, params: types_unique.CreateCollectionParams
    ) -> 'NFTCollection':
        params = params.copy()
        scale_params = {
            'mode': {'NFT': None},
            'name': [str2vec(params.pop('name'))],
            'description': [str2vec(params.pop('description'))],
            'token_prefix': params.pop('token_prefix'),
        }
        access = params.pop('access', None)
        if access is not None:
            access = {access: None}
        scale_params['access'] = access
        limits = params.pop('limits', None)
        if limits is not None:
            simple_limits = (
                'account_token_ownership_limit', 'sponsored_data_size', 'token_limit', 'sponsor_transfer_timeout',
                'sponsor_approve_timeout', 'owner_can_transfer', 'owner_can_destroy', 'transfers_enabled'
            )
            scale_limits = {
                x: limits.pop(x, None) for x in simple_limits
            }
            sponsored_data_rate_limit = limits.pop('sponsored_data_rate_limit', None)
            if sponsored_data_rate_limit == 'SponsoringDisabled':
                sponsored_data_rate_limit = {'SponsoringDisabled': None}
            if isinstance(sponsored_data_rate_limit, int):
                sponsored_data_rate_limit = {'Blocks': sponsored_data_rate_limit}
            scale_limits['sponsored_data_rate_limit'] = sponsored_data_rate_limit
        else:
            scale_limits = None
        scale_params['limits'] = scale_limits
        permissions = params.pop('permissions', None)
        if permissions is not None:
            scale_permissions = {}
            access = params.pop('access', None)
            if access is not None:
                access = {access: None}
            scale_permissions['access'] = access
            scale_permissions['mint_mode'] = permissions.pop('mint_mode', None)
            nesting = permissions.pop('nesting', None)
            if nesting is not None:
                restricted = nesting.pop('restricted', None)
                nesting['restricted'] = restricted
            scale_permissions['nesting'] = nesting
        else:
            scale_permissions = None
        scale_params['permissions'] = scale_permissions
        scale_params['token_property_permissions'] = [params.pop('token_property_permissions', [])]
        scale_params['properties'] = [params.pop('properties', [])]
        scale_params['admin_list'] = params.pop('admin_list', [])
        scale_params['pending_sponsor'] = params.pop('pending_sponsor', None)
        scale_params['flags'] = params.pop('flags', [0])

        receipt = self.helper.execute_extrinsic(signer, 'Unique.create_collection_ex', {'data': scale_params})

        event = self.helper.find_event('Common.CollectionCreated', receipt['events'])
        collection_id, collection_type, owner = event['attributes']

        return NFTCollection(self.helper, collection_id)

    def destroy_collection(self, signer: substrateinterface.Keypair, collection_id: int) -> bool:
        receipt = self.helper.execute_extrinsic(signer, 'Unique.destroy_collection', {'collection_id': collection_id})
        event = self.helper.find_event('Common.CollectionDestroyed', receipt['events'])
        return event is not None

    def mint_token(
        self, signer: substrateinterface.Keypair, collection_id: int, owner: types_unique.CrossAccountId,
        properties: list[types_unique.Property] | None = None
    ) -> 'NFTToken':
        receipt = self.helper.execute_extrinsic(signer, 'Unique.create_item', {
            'collection_id': collection_id,
            'owner': owner,
            'data': {
                'NFT': {
                    'properties': [([] if properties is None else properties)]
                }
            }
        })
        event = self.helper.find_event('Common.ItemCreated', receipt['events'])
        collection_id, token_id, owner, collection_type = event['attributes']
        return NFTToken(NFTCollection(self.helper, collection_id), token_id)

    def _extract_tokens_from_events(self, events: list[types_system.Event]) -> list['NFTToken']:
        tokens: list[NFTToken] = []
        for e in events:
            if e['module_id'] != 'Common' or e['event_id'] != 'ItemCreated':
                continue
            collection_id, token_id, owner, value = e['attributes']
            tokens.append(NFTToken(NFTCollection(self.helper, collection_id), token_id))
        return tokens

    def mint_multiple_tokens_simple(
        self, signer: substrateinterface.Keypair, collection_id: int, owner: types_unique.CrossAccountId,
        properties: list[list[types_unique.Property] | None]
    ) -> list['NFTToken']:
        receipt = self.helper.execute_extrinsic(signer, 'Unique.create_multiple_items', {
            'collection_id': collection_id,
            'owner': owner,
            'items_data': [
                {'NFT': {'properties': [[] if x is None else x]}} for x in properties
            ]
        })
        return self._extract_tokens_from_events(receipt['events'])

    def mint_multiple_tokens(
        self, signer: substrateinterface.Keypair, collection_id: int, tokens: list[types_unique.CreateTokenParams]
    ) -> list['NFTToken']:
        receipt = self.helper.execute_extrinsic(signer, 'Unique.create_multiple_items_ex', {
            'collection_id': collection_id,
            'data': {
                'NFT': [[
                    {
                        'properties': [[] if x['properties'] is None else x['properties']],
                        'owner': x['owner']
                    } for x in tokens
                ]]
            }
        })
        return self._extract_tokens_from_events(receipt['events'])

    def burn_token(self, signer: substrateinterface.Keypair, collection_id: int, token_id: int) -> bool:
        receipt = self.helper.execute_extrinsic(signer, 'Unique.burn_item', {
            'collection_id': collection_id,
            'item_id': token_id,
            'value': 1
        })
        event = self.helper.find_event('Common.ItemDestroyed', receipt['events'])
        return event is not None

    def transfer_token(
        self, signer: substrateinterface.Keypair, collection_id: int, token_id: int,
        receiver: types_unique.CrossAccountId
    ) -> bool:
        receipt = self.helper.execute_extrinsic(signer, 'Unique.transfer', {
            'collection_id': collection_id,
            'item_id': token_id,
            'value': 1,
            'recipient': receiver
        })
        event = self.helper.find_event('Common.Transfer', receipt['events'])
        return event is not None


class NFTCollection(object):
    def __init__(self, helper: UniqueHelper, collection_id: int):
        self.helper = helper
        self.collection_id = collection_id

    def get_info(self):
        return self.helper.nft.get_collection_info(self.collection_id)

    def get_token_info(self, token_id: int, property_keys: list[str] | None = None):
        return self.helper.nft.get_token_info(self.collection_id, token_id, property_keys)

    def destroy(self, signer: substrateinterface.Keypair):
        return self.helper.nft.destroy_collection(signer, self.collection_id)

    def mint_token(
        self, signer: substrateinterface.Keypair, owner: types_unique.CrossAccountId,
        properties: list[types_unique.Property] | None = None
    ):
        return self.helper.nft.mint_token(signer, self.collection_id, owner, properties)

    def mint_multiple_tokens_simple(
        self, signer: substrateinterface.Keypair, owner: types_unique.CrossAccountId,
        properties: list[list[types_unique.Property] | None]
    ):
        return self.helper.nft.mint_multiple_tokens_simple(signer, self.collection_id, owner, properties)

    def mint_multiple_tokens(self, signer: substrateinterface.Keypair, tokens: list[types_unique.CreateTokenParams]):
        return self.helper.nft.mint_multiple_tokens(signer, self.collection_id, tokens)

    def burn_token(self, signer: substrateinterface.Keypair, token_id: int):
        return self.helper.nft.burn_token(signer, self.collection_id, token_id)

    def transfer_token(self, signer: substrateinterface.Keypair, token_id: int, receiver: types_unique.CrossAccountId):
        return self.helper.nft.transfer_token(signer, self.collection_id, token_id, receiver)


class NFTToken(object):
    def __init__(self, collection: NFTCollection, token_id: int):
        self.collection = collection
        self.token_id = token_id

    def get_info(self, property_keys: list[str] | None = None):
        return self.collection.get_token_info(self.token_id, property_keys)

    def burn(self, signer: substrateinterface.Keypair):
        return self.collection.burn_token(signer, self.token_id)

    def transfer(self, signer: substrateinterface.Keypair, receiver: types_unique.CrossAccountId):
        return self.collection.transfer_token(signer, self.token_id, receiver)

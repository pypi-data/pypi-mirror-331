import time
import unittest


from unique_playgrounds import UniqueHelper


class NFTTestCase(unittest.TestCase):
    def test_create_collection(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            collection = helper.nft.create_collection(alice, {
                'name': 'test', 'description': 'test', 'token_prefix': 'TST',
                'token_property_permissions': [
                    {'key': 'a', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}},
                    {'key': 'b', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}}
                ],
                'properties': [{'key': 'prop', 'value': 'val'}]
            })
            info = collection.get_info()
            self.assertEqual(info, {
                'owner': '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
                'mode': 'NFT',
                'name': 'test',
                'description': 'test',
                'token_prefix': 'TST',
                'sponsorship': 'Disabled',
                'limits': {
                    'account_token_ownership_limit': None, 'sponsored_data_size': None,
                    'sponsored_data_rate_limit': None, 'token_limit': None, 'sponsor_transfer_timeout': None,
                    'sponsor_approve_timeout': None, 'owner_can_transfer': None, 'owner_can_destroy': None,
                    'transfers_enabled': None
                },
                'permissions': {
                    'access': 'Normal',
                    'mint_mode': False,
                    'nesting': {
                        'token_owner': False, 'collection_admin': False, 'restricted': None
                    }
                },
                'token_property_permissions': [
                    {'key': 'a', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}},
                    {'key': 'b', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}}
                ],
                'properties': [
                    {'key': 'prop', 'value': 'val'}
                ],
                'read_only': False,
                'flags': {'foreign': False, 'erc721metadata': False}
            })

    def test_destroy_collection(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            collection = helper.nft.create_collection_simple(alice, 'name', 'description', 'TST')
            info = collection.get_info()
            self.assertEqual(isinstance(info, dict), True)
            result = collection.destroy(alice)
            self.assertEqual(result, True)
            info = collection.get_info()
            self.assertEqual(info, None)

    def test_mint_token(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            john = helper.address.get_keypair('//John')
            collection = helper.nft.create_collection(alice, {
                'name': 'test', 'description': 'test', 'token_prefix': 'TST',
                'token_property_permissions': [
                    {'key': 'a', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}},
                    {'key': 'b', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}}
                ]
            })
            token = collection.mint_token(alice, {'Substrate': john.ss58_address}, [{'key': 'a', 'value': 'aaa'}])
            self.assertEqual(token.token_id, 1)
            info = token.get_info()
            self.assertEqual(info, {
                'owner': {'Substrate': '5Eydmaz2dPdTtQ3zze3owCDyf8tYNGK6RKMWFmTYvWzdUV6Q'},
                'properties': [{'key': 'a', 'value': 'aaa'}],
                'pieces': 1
            })
            token = collection.mint_token(alice, {'Substrate': john.ss58_address}, [{'key': 'b', 'value': 'bbb'}])
            self.assertEqual(token.token_id, 2)
            info = token.get_info(['b'])
            self.assertEqual(info, {
                'owner': {'Substrate': '5Eydmaz2dPdTtQ3zze3owCDyf8tYNGK6RKMWFmTYvWzdUV6Q'},
                'properties': [{'key': 'b', 'value': 'bbb'}],
                'pieces': 1
            })
            info = token.get_info(['a'])
            self.assertEqual(info, {
                'owner': {'Substrate': '5Eydmaz2dPdTtQ3zze3owCDyf8tYNGK6RKMWFmTYvWzdUV6Q'},
                'properties': [],
                'pieces': 1
            })
            token = collection.mint_token(alice, {'Substrate': john.ss58_address})
            self.assertEqual(token.token_id, 3)
            info = token.get_info()
            self.assertEqual(info, {
                'owner': {'Substrate': '5Eydmaz2dPdTtQ3zze3owCDyf8tYNGK6RKMWFmTYvWzdUV6Q'},
                'properties': [],
                'pieces': 1
            })

    def test_mint_multiple_tokens_simple(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            john = helper.address.get_keypair('//John')
            collection = helper.nft.create_collection(alice, {
                'name': 'test', 'description': 'test', 'token_prefix': 'TST',
                'token_property_permissions': [
                    {'key': 'a', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}},
                    {'key': 'b', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}}
                ]
            })
            tokens = collection.mint_multiple_tokens_simple(alice, {'Substrate': john.ss58_address}, [
                None, [{'key': 'a', 'value': 'aa'}], [{'key': 'b', 'value': 'bb'}]
            ])
            self.assertEqual(len(tokens), 3)
            self.assertEqual(tokens[0].token_id, 1)
            self.assertEqual(tokens[0].get_info(), {
                'owner': {'Substrate': helper.address.normalize(john.ss58_address)},
                'properties': [],
                'pieces': 1
            })
            self.assertEqual(tokens[1].token_id, 2)
            self.assertEqual(tokens[1].get_info(), {
                'owner': {'Substrate': helper.address.normalize(john.ss58_address)},
                'properties': [{'key': 'a', 'value': 'aa'}],
                'pieces': 1
            })
            self.assertEqual(tokens[2].token_id, 3)
            self.assertEqual(tokens[2].get_info(), {
                'owner': {'Substrate': helper.address.normalize(john.ss58_address)},
                'properties': [{'key': 'b', 'value': 'bb'}],
                'pieces': 1
            })

    def test_mint_multiple_tokens(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            john = helper.address.get_keypair('//John')
            collection = helper.nft.create_collection(alice, {
                'name': 'test', 'description': 'test', 'token_prefix': 'TST',
                'token_property_permissions': [
                    {'key': 'a', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}},
                    {'key': 'b', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}}
                ]
            })
            tokens = collection.mint_multiple_tokens(alice, [
                {'properties': None, 'owner': {'Substrate': john.ss58_address}},
                {'properties': [{'key': 'a', 'value': 'aa'}], 'owner': {'Substrate': john.ss58_address}},
                {'properties': [{'key': 'b', 'value': 'bb'}], 'owner': {'Substrate': john.ss58_address}}
            ])
            self.assertEqual(len(tokens), 3)
            self.assertEqual(tokens[0].token_id, 1)
            self.assertEqual(tokens[0].get_info(), {
                'owner': {'Substrate': helper.address.normalize(john.ss58_address)},
                'properties': [],
                'pieces': 1
            })
            self.assertEqual(tokens[1].token_id, 2)
            self.assertEqual(tokens[1].get_info(), {
                'owner': {'Substrate': helper.address.normalize(john.ss58_address)},
                'properties': [{'key': 'a', 'value': 'aa'}],
                'pieces': 1
            })
            self.assertEqual(tokens[2].token_id, 3)
            self.assertEqual(tokens[2].get_info(), {
                'owner': {'Substrate': helper.address.normalize(john.ss58_address)},
                'properties': [{'key': 'b', 'value': 'bb'}],
                'pieces': 1
            })

    def test_burn_token(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            john = helper.address.get_keypair(f'//John{int(time.time())}')
            helper.balance.transfer(alice, john.ss58_address, 100, in_tokens=True)
            collection = helper.nft.create_collection(alice, {
                'name': 'test', 'description': 'test', 'token_prefix': 'TST',
                'token_property_permissions': [
                    {'key': 'a', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}},
                    {'key': 'b', 'permission': {'mutable': False, 'collection_admin': True, 'token_owner': True}}
                ]
            })
            token = collection.mint_token(alice, {'Substrate': john.ss58_address}, [{'key': 'a', 'value': 'aaa'}])
            self.assertEqual(token.token_id, 1)
            result = token.burn(john)
            self.assertEqual(result, True)
            info = token.get_info()
            self.assertEqual(info, None)

    def test_transfer_token(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            john = helper.address.get_keypair('//John')
            collection = helper.nft.create_collection(alice, {
                'name': 'test', 'description': 'test', 'token_prefix': 'TST'
            })
            token = collection.mint_token(alice, {'Substrate': alice.ss58_address})
            info = token.get_info()
            self.assertEqual(info['owner']['Substrate'], helper.address.normalize(alice.ss58_address))
            result = token.transfer(alice, {'Substrate': john.ss58_address})
            self.assertEqual(result, True)
            info = token.get_info()
            self.assertEqual(info['owner']['Substrate'], helper.address.normalize(john.ss58_address))


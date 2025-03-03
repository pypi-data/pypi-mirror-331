import time
import unittest


from unique_playgrounds import UniqueHelper
from unique_playgrounds.types_system import AccountBalance


class BalanceTestCase(unittest.TestCase):
    def test_transfer(self):
        with UniqueHelper('ws://127.0.0.1:9944') as helper:
            alice = helper.address.get_keypair('//Alice')
            john = helper.address.get_keypair(f'//John{int(time.time())}')
            balance = helper.balance.get_substrate(john.ss58_address)
            self.assertEqual(balance, AccountBalance(0, 0, 0))
            TO_TRANSFER = 100_000_000_000_000_000_000
            helper.balance.transfer(alice, john.ss58_address, TO_TRANSFER, in_tokens=False)
            balance = helper.balance.get_substrate(john.ss58_address)
            self.assertEqual(balance, AccountBalance(free=TO_TRANSFER, frozen=0, reserved=0))

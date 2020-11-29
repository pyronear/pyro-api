import unittest

from pyroclient import client


class ClientTester(unittest.TestCase):

    def test_client(self):

        self.assertRaises(Exception, client.Client, "http://localhost:8002", "invalid_login", "invalid_pwd")


if __name__ == '__main__':
    unittest.main()

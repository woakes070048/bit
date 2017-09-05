from unittest import TestCase
# from unittest.mock import Mock, patch
# from mock import Mock, patch
# from mock import MagicMock
from bit.models.connector import Connector


# Test Connector Model
class TestConnectorModel(TestCase):

    def setUp(self):
        self.connector = Connector()
        self.connector.name = 'NewConnectorName'
        self.connector.type = 'NewConnectorType'

    def test_repr(self):
        self.assertEqual(self.connector.__repr__(), '%s [%s]' % (
            self.connector.type,
            self.connector.name
        ))

    def test_get_data_sources(self):
        with self.assertRaises(NotImplementedError):
            self.connector.get_data_sources()

    def test_get_admin_data_sources(self):
        with self.assertRaises(NotImplementedError):
            self.connector.get_admin_data_sources()

    def test_get_columns(self):
        with self.assertRaises(NotImplementedError):
            self.connector.get_columns()

    def test_get_data(self):
        with self.assertRaises(NotImplementedError):
            self.connector.get_data()

# coding=UTF-8
import os, sys
test_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(test_folder, '.'))
sys.path.append(os.path.join(test_folder, '..'))

import logging
import mock
import unittest

from config import config
from loke import Loke

class LokeTestCase(unittest.TestCase):
    def setUp(self):
        config['db'] = os.path.join(test_folder, 'db.sqlite')
        config['auto_response'] = os.path.join(test_folder, '..', 'auto_response.json')
        self.sc_mock = mock.Mock()
        self.loke = Loke()
        self.loke.sc = self.sc_mock

    def test_no_auto_response_no_fjasefisken(self):
        self.loke.handle_message( {'user': 'U0HCKMF7B', 'text': 'Fjase fisken fjaser om fjasefisken', 'channel': 'general'})
        assert not self.sc_mock.api_call.called, 'method should not have been called'

    def test_auto_response_to_snylteagurk(self):
        self.loke.handle_message( {'user': 'U0HCKMF7B', 'text': 'hello snylteagurk tror jeg', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Sylteagurk er gr\xc3\xb8nnsaken som tok drepen p\xc3\xa5 de norr\xc3\xb8ne gudene...')

    def test_auto_response_with_exact_match(self):
        self.loke.handle_message( {'user': 'U0HCKMF7B', 'text': 'Dro en tur', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Turan som t\xc3\xa6lle!!')

    def test_auto_response_with_comma(self):
        self.loke.handle_message( {'user': 'U0HCKMF7B', 'text': 'Dro en tur, med komma', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Turan som t\xc3\xa6lle!!')

    def test_auto_response_multiple_match(self):
        self.loke.handle_message( {'user': 'U0HCKMF7B', 'text': 'hello snylteagurk tror jeg sylteagurk', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Sylteagurk er gr\xc3\xb8nnsaken som tok drepen p\xc3\xa5 de norr\xc3\xb8ne gudene...')

    def test_auto_response_no_ratio_match_for_tur(self):
        self.loke.handle_message( {'user': 'U0HCKMF7B', 'text': 'utur', 'channel': 'general'})
        assert not self.sc_mock.api_call.called, 'method should not have been called'

    def test_handle_presence_change_valid(self):
        self.loke.handle_presence_change( {'user': 'dummy', 'presence': 'active'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel=config['chan_general'], text='<@dummy> is alive!! Skal han booke fly mon tro?!')

    def test_handle_presence_change_rate_limit(self):
        self.loke.handle_presence_change( {'user': 'dummy', 'presence': 'active'})
        self.loke.handle_presence_change( {'user': 'dummy', 'presence': 'active'})
        self.loke.handle_presence_change( {'user': 'dummy', 'presence': 'active'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel=config['chan_general'], text='<@dummy> is alive!! Skal han booke fly mon tro?!')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

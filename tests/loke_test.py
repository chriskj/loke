# coding=UTF-8
import os, sys
test_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(test_folder, '.'))
sys.path.append(os.path.join(test_folder, '..'))

import logging
import mock
import unittest

from configobj import ConfigObj
import loke

class LokeTestCase(unittest.TestCase):
    def setUp(self):
        self.config = ConfigObj(os.path.join(test_folder, 'config.ini'))
        self.config['db'] = os.path.join(test_folder, 'db.sqlite')
        self.sc_mock = mock.Mock()

    def test_no_auto_response_no_fjasefisken(self):
        loke.handle_message(self.config, self.sc_mock,
                {'user': 'U0HCKMF7B', 'text': 'Fjase fisken fjaser om fjasefisken', 'channel': 'general'})
        assert not self.sc_mock.api_call.called, 'method should not have been called'

    def test_auto_response_to_snylteagurk(self):
        loke.handle_message(self.config, self.sc_mock,
                {'user': 'U0HCKMF7B', 'text': 'hello snylteagurk tror jeg', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Sylteagurk er gr\xc3\xb8nnsaken som tok drepen p\xc3\xa5 de norr\xc3\xb8ne gudene...')

    def test_auto_response_multiple_match(self):
        loke.handle_message(self.config, self.sc_mock,
                {'user': 'U0HCKMF7B', 'text': 'hello snylteagurk tror jeg sylteagurk', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Sylteagurk er gr\xc3\xb8nnsaken som tok drepen p\xc3\xa5 de norr\xc3\xb8ne gudene...')

    def test_auto_response_with_comma(self):
        loke.handle_message(self.config, self.sc_mock,
                {'user': 'U0HCKMF7B', 'text': 'Hva med sylteagurk, komma?', 'channel': 'general'})
        self.sc_mock.api_call.assert_called_once_with("chat.postMessage", as_user="true:",
                channel='general', text='Sylteagurk er gr\xc3\xb8nnsaken som tok drepen p\xc3\xa5 de norr\xc3\xb8ne gudene...')

    def test_auto_response_no_ratio_match_for_tur(self):
        loke.handle_message(self.config, self.sc_mock,
                {'user': 'U0HCKMF7B', 'text': 'utur', 'channel': 'general'})
        assert not self.sc_mock.api_call.called, 'method should not have been called'

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

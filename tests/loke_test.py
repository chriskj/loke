# coding=UTF-8
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock


TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(TEST_FOLDER, '..'))

from loke import Loke  # noqa: E402


class RecordingHandler:
    def __init__(self):
        self.messages = []
        self.presence_events = []

    def handler_version(self):
        return "Recording"

    def handle_message(self, event):
        self.messages.append(event)

    def handle_presence_change(self, event):
        self.presence_events.append(event)


class LokeTestCase(unittest.TestCase):
    def setUp(self):
        self.loke = Loke({'ownid': 'U_BOT'})
        self.loke.sc = mock.Mock()
        self.handler = RecordingHandler()
        self.loke.register_handler(self.handler)

    def test_dispatches_normal_message(self):
        event = {'user': 'U_USER', 'text': '.hello', 'channel': 'C1'}

        self.loke.handle_message(event)

        self.assertEqual([event], self.handler.messages)

    def test_ignores_bot_and_message_change_events(self):
        self.loke.handle_message(
            {'bot_id': 'B1', 'text': '.hello', 'channel': 'C1'}
        )
        self.loke.handle_message(
            {
                'user': 'U_USER',
                'subtype': 'message_changed',
                'text': '.hello',
                'channel': 'C1',
            }
        )

        self.assertEqual([], self.handler.messages)

    def test_modules_command_uses_modern_chat_post_message(self):
        self.loke.handle_message(
            {'user': 'U_USER', 'text': '.modules', 'channel': 'C1'}
        )

        self.loke.sc.chat_postMessage.assert_called_once_with(
            channel='C1', text='*Loaded modules*\n - Recording'
        )

    def test_socket_mode_request_is_acknowledged_and_dispatched(self):
        client = mock.Mock()
        request = SimpleNamespace(
            envelope_id='env-1',
            type='events_api',
            payload={
                'event': {
                    'type': 'message',
                    'user': 'U_USER',
                    'text': '.hello',
                    'channel': 'C1',
                }
            },
        )

        self.loke._process_socket_mode_request(client, request)

        response = client.send_socket_mode_response.call_args.args[0]
        self.assertEqual('env-1', response.envelope_id)
        self.assertEqual(1, len(self.handler.messages))

    @mock.patch('loke.SocketModeClient')
    @mock.patch('loke.WebClient')
    def test_init_uses_environment_tokens(self, web_client, socket_client):
        socket_client.return_value.socket_mode_request_listeners = []
        with mock.patch.dict(
            os.environ,
            {
                'SLACK_BOT_TOKEN': 'xoxb-test',
                'SLACK_APP_TOKEN': 'xapp-test',
            },
        ):
            initialized = Loke({}).init()

        web_client.assert_called_once_with(token='xoxb-test')
        socket_client.assert_called_once_with(
            app_token='xapp-test', web_client=web_client.return_value
        )
        self.assertIn(
            initialized._process_socket_mode_request,
            socket_client.return_value.socket_mode_request_listeners,
        )

    def test_init_reports_missing_credentials(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'SLACK_BOT_TOKEN.*SLACK_APP_TOKEN'):
                Loke({}).init()


if __name__ == '__main__':
    unittest.main()

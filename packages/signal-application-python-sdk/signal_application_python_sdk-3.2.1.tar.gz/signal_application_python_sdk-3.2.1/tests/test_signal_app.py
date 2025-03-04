from unittest.mock import patch, MagicMock
from unittest import TestCase
import pytest
from signalsdk.signal_app import SignalApp
from signalsdk.config import (
    LOCALMQTT_SDK_TOPIC_PREFIX,
    LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC,
)


@patch("signalsdk.signal_app.get_app_config_api")
@patch("signalsdk.signal_app.LocalMqtt.publish")
@patch("signalsdk.signal_app.LocalMqtt.connect")
@patch("signalsdk.signal_app.os.getenv")
class Test_Signal_App(TestCase):
    mock_event_cb = MagicMock()
    mock_config_change_cb = MagicMock()
    mock_command_cb = MagicMock()

    def test_app_initialize_ok_without_cmd_callback(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }

        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()

    def test_app_initialize_ok_with_only_config_callback(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }

        sig_app.initialize(self.mock_config_change_cb)
        mock_localMqtt.assert_called()

    def test_app_initialize_ok_with_cmd_callback(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }

        sig_app.initialize(
            self.mock_config_change_cb, self.mock_event_cb, self.mock_command_cb
        )
        mock_localMqtt.assert_called()

    def test_app_initialize_no_app_id(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = None
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }

        with pytest.raises(BaseException):
            sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_not_called()

    def test_app_initialize_no_settings(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {}
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()

    def test_app_on_event_received_handler(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()
        sig_app._SignalApp__on_event_received_handler("event")
        self.mock_event_cb.assert_called()

    def test_app_on_command_received_handler(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }
        sig_app.initialize(
            self.mock_config_change_cb, self.mock_event_cb, self.mock_command_cb
        )
        mock_localMqtt.assert_called()
        sig_app._SignalApp__on_command_received_handler("event")
        self.mock_command_cb.assert_called()

    @patch("signalsdk.signal_app.LocalMqtt.subscribe")
    @patch("signalsdk.signal_app.LocalMqtt.set_on_event_received")
    def test_app_listening_app_config_updates(
        self,
        mock_set_on_event_received,
        mock_subscribe,
        mock_env,
        mock_localMqtt,
        mock_localpub,
        mock_get_app,
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()
        sig_app._SignalApp__start_listening_app_config_updates()
        mock_get_app.assert_called()
        # check set_on_event_receive called twice for app config and sdk config
        self.assertEqual(mock_set_on_event_received.call_count, 5)
        # check set_on_event_receive called with app config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            sig_app._SignalApp__on_config_updated_handler,
        )
        # check set_on_event_receive called with sdk config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_TOPIC_PREFIX + "12345",
            sig_app._SignalApp__on_event_received_handler,
        )
        # check subscribe called twice for app config and sdk config
        self.assertEqual(mock_subscribe.call_count, 5)
        # check subscribe called with app config topic
        mock_subscribe.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            False,
        )
        # check subscribe called with sdk config topic
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345", False)
        self.mock_config_change_cb.assert_called()
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345_out", False)
        self.mock_config_change_cb.assert_called()

    def test_app_next_notopic(
        self, mock_env, mock_localMqtt, mock_localpub, mock_get_app
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_event = MagicMock()
        sig_app.next(mock_event)
        mock_localpub.assert_not_called()

    def test_app_broadcast(self, mock_env, mock_localMqtt, mock_localpub, mock_get_app):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}]
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_event = MagicMock()
        sig_app.broadcast(mock_event)
        mock_localpub.assert_called_with(
            LOCALMQTT_SDK_TOPIC_PREFIX + "broadcast", mock_event
        )

    @patch("signalsdk.signal_app.LocalMqtt.subscribe")
    @patch("signalsdk.signal_app.LocalMqtt.set_on_event_received")
    def test_app_next_no_pub_topic(
        self,
        mock_set_on_event_received,
        mock_subscribe,
        mock_env,
        mock_localMqtt,
        mock_localpub,
        mock_get_app,
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}],
            "settingsForSDK": {"sdkPubTopic": ""},
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()
        sig_app._SignalApp__start_listening_app_config_updates()
        mock_get_app.assert_called()
        # check set_on_event_receive called twice for app config and sdk config
        self.assertEqual(mock_set_on_event_received.call_count, 5)
        # check set_on_event_receive called with app config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            sig_app._SignalApp__on_config_updated_handler,
        )
        # check set_on_event_receive called with sdk config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_TOPIC_PREFIX + "12345",
            sig_app._SignalApp__on_event_received_handler,
        )
        # check subscribe called twice for app config and sdk config
        self.assertEqual(mock_subscribe.call_count, 5)
        # check subscribe called with app config topic
        mock_subscribe.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            False,
        )
        # check subscribe called with sdk config topic
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345", False)

        self.mock_config_change_cb.assert_called()
        mock_event = MagicMock()
        sig_app.next(mock_event)
        mock_localpub.assert_not_called()

    @patch("signalsdk.signal_app.LocalMqtt.subscribe")
    @patch("signalsdk.signal_app.LocalMqtt.set_on_event_received")
    def test_app_next_with_pub_topic(
        self,
        mock_set_on_event_received,
        mock_subscribe,
        mock_env,
        mock_localMqtt,
        mock_localpub,
        mock_get_app,
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}],
            "settingsForSDK": {"sdkPubTopic": "value2"},
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()
        sig_app._SignalApp__start_listening_app_config_updates()
        mock_get_app.assert_called()
        # check set_on_event_receive called twice for app config and sdk config
        self.assertEqual(mock_set_on_event_received.call_count, 5)
        # check set_on_event_receive called with app config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            sig_app._SignalApp__on_config_updated_handler,
        )
        # check set_on_event_receive called with sdk config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_TOPIC_PREFIX + "12345",
            sig_app._SignalApp__on_event_received_handler,
        )
        # check subscribe called twice for app config and sdk config
        self.assertEqual(mock_subscribe.call_count, 5)
        # check subscribe called with app config topic
        mock_subscribe.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            False,
        )
        # check subscribe called with sdk config topic
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345", False)
        self.mock_config_change_cb.assert_called()
        mock_event = MagicMock()
        sig_app.next(mock_event)
        mock_localpub.assert_called_with(
            LOCALMQTT_SDK_TOPIC_PREFIX + "value2", mock_event
        )

    @patch("signalsdk.signal_app.LocalMqtt.subscribe")
    @patch("signalsdk.signal_app.LocalMqtt.set_on_event_received")
    def test_app_nextNode_with_pub_topic(
        self,
        mock_set_on_event_received,
        mock_subscribe,
        mock_env,
        mock_localMqtt,
        mock_localpub,
        mock_get_app,
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}],
            "settingsForSDK": {"sdkPubTopic": "value2"},
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()
        sig_app._SignalApp__start_listening_app_config_updates()
        mock_get_app.assert_called()
        # check set_on_event_receive called twice for app config and sdk config
        self.assertEqual(mock_set_on_event_received.call_count, 5)
        # check set_on_event_receive called with app config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            sig_app._SignalApp__on_config_updated_handler,
        )
        # check set_on_event_receive called with sdk config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_TOPIC_PREFIX + "12345",
            sig_app._SignalApp__on_event_received_handler,
        )
        # check subscribe called twice for app config and sdk config
        self.assertEqual(mock_subscribe.call_count, 5)
        # check subscribe called with app event topics
        mock_subscribe.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            False,
        )
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345", False)
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345_out", False)
        self.mock_config_change_cb.assert_called()

        mock_event = MagicMock()
        sig_app.nextNode(mock_event)
        mock_localpub.assert_called_with(
            LOCALMQTT_SDK_TOPIC_PREFIX + "12345_out", mock_event
        )

    @patch("signalsdk.signal_app.LocalMqtt.subscribe")
    @patch("signalsdk.signal_app.LocalMqtt.set_on_event_received")
    def test_app_next_with_app_id(
        self,
        mock_set_on_event_received,
        mock_subscribe,
        mock_env,
        mock_localMqtt,
        mock_localpub,
        mock_get_app,
    ):
        sig_app = SignalApp()
        mock_env.return_value = "12345"
        mock_get_app.return_value = {
            "settingsForApp": [{"key": "key1", "value": "value1"}],
            "settingsForSDK": {"sdkPubTopic": "value2"},
        }
        sig_app.initialize(self.mock_config_change_cb, self.mock_event_cb)
        mock_localMqtt.assert_called()
        sig_app._SignalApp__start_listening_app_config_updates()
        mock_get_app.assert_called()
        # check set_on_event_receive called twice for app config and sdk config
        self.assertEqual(mock_set_on_event_received.call_count, 5)
        # check set_on_event_receive called with app config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            sig_app._SignalApp__on_config_updated_handler,
        )
        # check set_on_event_receive called with sdk config topic
        mock_set_on_event_received.assert_any_call(
            LOCALMQTT_SDK_TOPIC_PREFIX + "12345",
            sig_app._SignalApp__on_event_received_handler,
        )
        # check subscribe called twice for app config and sdk config
        self.assertEqual(mock_subscribe.call_count, 5)
        # check subscribe called with app config topic
        mock_subscribe.assert_any_call(
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace("${appId}", "12345"),
            False,
        )
        # check subscribe called with sdk config topic
        mock_subscribe.assert_any_call(LOCALMQTT_SDK_TOPIC_PREFIX + "12345", False)
        self.mock_config_change_cb.assert_called()
        mock_event = MagicMock()
        sig_app.next(mock_event, "56789")
        mock_localpub.assert_called_with(
            LOCALMQTT_SDK_TOPIC_PREFIX + "56789", mock_event
        )

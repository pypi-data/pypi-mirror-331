from unittest.mock import patch
from requests.exceptions import HTTPError
from signalsdk import api


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise HTTPError


@patch("requests.get")
@patch("os.getenv")
def test_get_app_config(mock_os, mock_get):
    mock_os.return_value = None
    fake_response = MockResponse(None, status_code=200)
    mock_get.return_value = fake_response
    appId = "mockAppId"
    result = api.get_app_config_api(appId)
    mock_get.assert_called_once_with(
        api.API_APPS_CONFIG_URL.format(5000),
        params={"applicationId": appId},
        timeout=30,
    )
    assert result is None


@patch("requests.get")
@patch("os.getenv")
def test_get_app_config_alternative_port(mock_os, mock_get):
    port = 5001
    mock_os.return_value = port
    fake_response = MockResponse(None, status_code=200)
    mock_get.return_value = fake_response
    appId = "mockAppId"
    result = api.get_app_config_api(appId)
    mock_get.assert_called_once_with(
        api.API_APPS_CONFIG_URL.format(port),
        params={"applicationId": appId},
        timeout=30,
    )
    assert result is None


@patch("requests.get")
@patch("os.getenv")
def test_get_app_config_alternative_port_passed_in(mock_os, mock_get):
    port = 6000
    mock_os.return_value = None
    fake_response = MockResponse(None, status_code=200)
    mock_get.return_value = fake_response
    appId = "mockAppId"
    result = api.get_app_config_api(appId, port=port)
    mock_get.assert_called_once_with(
        api.API_APPS_CONFIG_URL.format(port),
        params={"applicationId": appId},
        timeout=30,
    )
    assert result is None


@patch("requests.get")
@patch("os.getenv")
def test_get_app_config_good_data(mock_os, mock_get):
    mock_os.return_value = None
    fake_response = MockResponse({"thingName": "unit_test_thing"}, status_code=200)
    mock_get.return_value = fake_response
    appId = "mockAppId"
    result = api.get_app_config_api(appId)
    mock_get.assert_called_once_with(
        api.API_APPS_CONFIG_URL.format(5000),
        params={"applicationId": appId},
        timeout=30,
    )
    assert result["thingName"] == "unit_test_thing"


@patch("requests.get")
@patch("os.getenv")
@patch("time.sleep")
def test_get_app_config_raise_error(mock_sleep, mock_os, mock_get):
    mock_os.return_value = None
    fake_response = MockResponse({}, status_code=400)
    mock_get.return_value = fake_response
    appId = "mockAppId"
    api.get_app_config_api(appId)
    assert mock_get.call_count == api.MAX_RETRIES
    # check every call has the correct params
    for call in mock_get.call_args_list:
        args, kwargs = call
        assert args[0] == api.API_APPS_CONFIG_URL.format(5000)
        assert kwargs["params"]["applicationId"] == appId
        assert kwargs["timeout"] == 30
    assert mock_sleep.call_count == api.MAX_RETRIES
    # check every call has the correct params
    i = 0
    for call in mock_sleep.call_args_list:
        args, kwargs = call
        assert args[0] == api.RETRY_DELAY + 2 * i
        i += 1


@patch("requests.get")
@patch("os.getenv")
def test_get_device_config_data(mock_os, mock_get):
    mock_os.return_value = None
    fake_response = MockResponse(
        {"deviceId": "fake_device_id", "accountId": "fake_account_id"}, status_code=200
    )
    mock_get.return_value = fake_response
    result = api.get_device_config_api()
    mock_get.assert_called_once_with(
        api.API_DEVICE_CONFIG_URL.format(5000), params=None, timeout=30
    )
    assert result["deviceId"] == "fake_device_id"
    assert result["accountId"] == "fake_account_id"

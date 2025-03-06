import os
import urllib.request
import urllib.error
import json
from typing import Dict, Optional
import threading
from logging import getLogger

from dynamic_settings.types import JsonType, ValueType, BoolType, SettingsValueType, BOOL_TYPE_TO_PYTHON_BOOL
from dynamic_settings.errors import DynamicSettingsValidationError, DynamicSettingsFetchError

logger = getLogger(__name__)
_LOGGER_PREFIX = "[dynamic-settings]"


class DynamicSettings:
    """Fetch and manage dynamic settings from an external source."""
    _storage: Dict[str, ValueType] = {}

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        update_every: int = 10
    ) -> None:
        """
        Initialize the DynamicSettings client.

        :param url: The URL to fetch settings from. If not provided, it is read from the
                    DYNAMIC_SETTINGS_URL environment variable.
        :param api_key: The API key for authentication. If not provided, it is read from the
                        DYNAMIC_SETTINGS_API_KEY environment variable.
        :param update_every: The interval in seconds to fetch settings from the source.
        :raises ValueError: If either url or api_key is not provided.
        """
        url = url or os.getenv('DYNAMIC_SETTINGS_URL')
        if not url:
            raise ValueError(
                'The `url` option must be set either by passing `url` to the client '
                'or by setting the `DYNAMIC_SETTINGS_URL` environment variable'
            )
        url = url.strip().rstrip('/')
        self.url = url

        api_key = api_key or os.getenv("DYNAMIC_SETTINGS_API_KEY")
        if not api_key:
            raise ValueError(
                'The `api_key` option must be set either by passing `api_key` to the client '
                'or by setting the `DYNAMIC_SETTINGS_API_KEY` environment variable'
            )
        self.api_key = api_key
        self._update_every = update_every

        self._stop_event = threading.Event()
        self._initial_fetch_complete = threading.Event()

        self._refresh_thread = threading.Thread(target=self._refresh, daemon=True)
        self._refresh_thread.start()

    def _refresh(self) -> None:
        """
        Background thread that refreshes settings every `update_every` seconds.
        """

        while not self._stop_event.is_set():
            self._fetch_settings()
            self._stop_event.wait(self._update_every)

    def _fetch_settings(self) -> None:
        """
        Fetch settings from the external source and update internal storage.
        Handles any errors that occur during the fetch process.
        """
        try:
            self._fetch_settings_from_external_source()
            if not self._initial_fetch_complete.is_set():
                self._initial_fetch_complete.set()

        except Exception as e:
            logger.error("%s Background refresh error: %s", _LOGGER_PREFIX, e)

    def _fetch_settings_from_external_source(self) -> None:
        """
        Fetch settings from the external source and update internal storage.

        :raises DynamicSettingsFetchError: If the settings cannot be fetched.
        :raises DynamicSettingsValidationError: If the received data is not in the expected format.
        """
        logger.info("%s Fetching settings", _LOGGER_PREFIX)

        headers = {"X-API-KEY": self.api_key}
        url = f"{self.url}/api/v1/settings"
        try:
            r = self._make_request(url=url, headers=headers)
        except DynamicSettingsFetchError:
            raise

        try:
            settings = json.loads(r)
        except json.JSONDecodeError:
            raise DynamicSettingsValidationError("Invalid JSON response")

        for s in settings:
            key = s['key']
            raw_value = s['value']
            value_type = SettingsValueType(s['type'])

            try:
                value = self._parse_value(raw_value=raw_value, value_type=value_type)
            except DynamicSettingsValidationError as e:
                logger.error("%s %s %s", _LOGGER_PREFIX, key, e)
                continue

            self._storage[key] = value

    @staticmethod
    def _make_request(url: str, headers: Dict[str, str]) -> JsonType:
        """
        Make an HTTP request
        :param url: The URL.
        :param headers: The headers to send with the request.
        :return: The response data.
        """
        req = urllib.request.Request(url=url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read()
            return data
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            raise DynamicSettingsFetchError(f"Failed to fetch settings: {e}")

    @staticmethod
    def _parse_value(raw_value: str, value_type: SettingsValueType) -> ValueType:
        """
        Convert the value to the expected type based on setting_type.

        :param raw_value: The raw value from the settings source.
        :param value_type: The expected type for the value.
        :return: The value converted to the proper type.
        :raises DynamicSettingsValidationError: If the value is invalid.
        """
        if value_type == SettingsValueType.STRING:
            return str(raw_value)

        if value_type == SettingsValueType.INTEGER:
            try:
                return int(raw_value)
            except ValueError:
                raise DynamicSettingsValidationError(f"Invalid integer value: {raw_value}")

        if value_type == SettingsValueType.FLOAT:
            try:
                return float(raw_value)
            except ValueError:
                raise DynamicSettingsValidationError(f"Invalid float value: {raw_value}")

        if value_type == SettingsValueType.BOOLEAN:
            try:
                return BOOL_TYPE_TO_PYTHON_BOOL[BoolType(raw_value)]
            except ValueError:
                raise DynamicSettingsValidationError(f"Invalid boolean value: {raw_value}")

        if value_type == SettingsValueType.JSON:
            try:
                return json.loads(raw_value)
            except json.JSONDecodeError:
                raise DynamicSettingsValidationError(f"Invalid JSON value: {raw_value}")

        raise DynamicSettingsValidationError(f"Invalid setting type: {value_type}")

    def get(self, key: str, default: Optional[ValueType] = None) -> Optional[ValueType]:
        """
        Retrieve the value for a given setting key.

        :param key: The key of the setting.
        :param default: A default value if the key is not found.
        :return: The value of the setting, or default if not found.
        """
        self._initial_fetch_complete.wait(timeout=self._update_every)
        return self._storage.get(key, default)

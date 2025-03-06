class DynamicSettingsValidationError(Exception):
    """Raised when a setting value is invalid."""


class DynamicSettingsFetchError(Exception):
    """Raised when settings cannot be fetched."""

"""
Configuration provider to fetch values using env vars and external provider
"""

from value_fetcher import ValueFetcher

class ConfigProvider:
    """
    Configuration provider class
    """
    def __init__(self) -> None:
        self.env_defaults = {
            "REQUIRED_FIELDS": '',
            "HCAPTCHA_ENABLE": 'False',
            "HCAPTCHA_RESPONSE_FIELD": 'captcha-response',
            "HCAPTCHA_VERIFY_URL": 'https://hcaptcha.com/siteverify',
            "DYNAMODB_ENABLE": 'False',
            "EMAIL_ENABLE": 'False',
            "DISCORD_ENABLE": 'False',
            "SLACK_ENABLE": 'False',
        }

        self.value_fetcher = ValueFetcher(self.env_defaults)


    def configure(self) -> None:
        """
        Configure value fetcher as provider
        """


    def get(self, key: str) -> str:
        """
        Given a key name MY_VAL, check for a source env var e.g. MY_VAL_SOURCE.
        Raises exception if source does not match list of known services.
        """

        return self.value_fetcher.get(key)

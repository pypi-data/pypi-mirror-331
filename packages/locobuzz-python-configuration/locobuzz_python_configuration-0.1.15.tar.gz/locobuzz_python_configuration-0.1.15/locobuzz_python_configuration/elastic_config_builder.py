from typing import Any, Dict


class InvalidElasticConfigurationError(Exception):
    pass


class ElasticSearchConfigurationBuilder:
    def __init__(self, config: Any) -> None:
        self._config = config

    def build(self, data: Dict[str, Any]) -> None:
        self._config._elastic_host = data.get('elastic_host')
        self._config._elastic_username = data.get('elastic_username')
        self._config._elastic_password = data.get('elastic_password')

# async_helpers.py
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

from locobuzz_python_configuration.logger_config import setup_logger
from locobuzz_python_configuration.redis_client import RedisClientFactory
from locobuzz_python_configuration.utils_functions import setup_google_chat_messenger


@dataclass
class LoggerConfig:
    logger: Any
    log_enabled: List[str]

    def __iter__(self):
        yield self.logger
        yield self.log_enabled


async def configure_logger(service_name: str, configuration: Dict[str, Any]) -> LoggerConfig:
    is_async_logger = configuration.get('_is_async_logger', False)
    log_level = configuration['_log_level']
    logger = setup_logger(service_name, async_mode=is_async_logger, log_level_str=log_level)
    logger.info("Logger configured" + (" in async mode" if is_async_logger else ""))
    log_enabled = configuration.get('_log_enabled', "PRODUCTION").split(",")
    logger.info(f"Log enabled for environment: {log_enabled}")
    return LoggerConfig(logger=logger, log_enabled=log_enabled)


@dataclass
class GoogleChatConfig:
    g_chat: Any

    def __iter__(self):
        yield self.g_chat


async def configure_google_chat(service_name: str, configuration: Dict[str, Any],
                                environ: Any, log_enabled: List[str], logger: Any) -> GoogleChatConfig:
    extra_properties = configuration.get('_extra_properties', {})
    is_async_gchat = extra_properties.get("is_async_gchat", False)
    g_chat_hook = extra_properties.get("g_chat_webhook")
    error_gchat_hook = extra_properties.get("error_g_chat_webhook")
    logger.info(f"Google Chat async mode: {is_async_gchat}")
    logger.info(f"Google Chat webhook: {g_chat_hook}")
    logger.info(f"Error Google Chat webhook: {error_gchat_hook}")

    g_chat = setup_google_chat_messenger(
        service_name, g_chat_hook, error_gchat_hook, environ,
        is_async_gchat, log_enabled, logger
    )
    return GoogleChatConfig(g_chat=g_chat)


async def configure_clickhouse(configuration: Dict[str, Any], environ: str, logger) -> Dict[str, Any]:
    """
    Configures ClickHouse authentication based on the environment.
    - Production: Secure connection with verification enabled.
    - Staging: Secure connection disabled, unless valid credentials are provided.
    """

    clickhouse_host = configuration.get('_clickhouse_host')
    clickhouse_port = configuration.get('_clickhouse_port')
    clickhouse_username = configuration.get('_clickhouse_username')
    clickhouse_password = configuration.get('_clickhouse_password')

    logger.info(f"Configuring ClickHouse for {environ.upper()} environment.")

    if not clickhouse_host or not clickhouse_port:
        logger.error("Missing ClickHouse host or port in configuration.")
        raise ValueError("Missing ClickHouse host or port in configuration.")

    secure_connection = environ.lower() == "production"
    requires_auth = (
            clickhouse_username and clickhouse_password and
            clickhouse_username != "CLICKHOUSE_WRITE_USERNAME" and
            clickhouse_password != "CLICKHOUSE_WRITE_PASS_WORD"
    )

    if secure_connection and not requires_auth:
        logger.error("Invalid ClickHouse credentials in production.")
        raise ValueError("Invalid ClickHouse username or password in production.")

    auth_config = {
        'host': clickhouse_host,
        'port': clickhouse_port,
        'secure': secure_connection,
        'verify': secure_connection,
        'max_query_size': 20000000
    }

    if requires_auth:
        auth_config.update({'username': clickhouse_username, 'password': clickhouse_password})

    logger.info(f"ClickHouse connection configured successfully for {environ.upper()}.")
    return auth_config


@dataclass
class KafkaConfig:
    broker: Any
    read_topic: Any
    push_topic: Optional[Any]
    consumer_group_id: Optional[Any]

    def __iter__(self):
        yield self.broker
        yield self.read_topic
        yield self.push_topic
        yield self.consumer_group_id


async def configuration_kafka(configuration: Dict[str, Any]) -> KafkaConfig:
    broker = configuration['_broker']
    read_topic = configuration['_read_topic']
    push_topic = configuration.get("_push_topic")
    consumer_group_id = configuration.get("_extra_properties", {}).get("consumer_group_id")
    return KafkaConfig(
        broker=broker,
        read_topic=read_topic,
        push_topic=push_topic,
        consumer_group_id=consumer_group_id
    )


@dataclass
class DBConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


async def configure_db_auth(configuration: Dict[str, Any], database_name: str) -> DBConfig:
    """
    Retrieves authentication details for the database from the configuration.
    Expected keys: sql_server_ip, sql_user_name, sql_pass_word.
    The database name is passed as a parameter.
    """
    sql_server_ip = configuration.get("_sql_server_ip")
    sql_user_name = configuration.get("_sql_user_name")
    sql_pass_word = configuration.get("_sql_pass_word")

    # Extract host and port from sql_server_ip (assuming it's in "IP,PORT" format)
    if "," in sql_server_ip:
        host, port = sql_server_ip.split(",")
        port = int(port)  # Convert port to integer
    else:
        host = sql_server_ip
        port = 1433  # Default SQL Server port

    return DBConfig(
        host=host,
        port=port,
        username=sql_user_name,
        password=sql_pass_word,
        database=database_name
    )


@dataclass
class RedisConfig:
    redis_obj: Any

    def __iter__(self):
        yield self.redis_obj


def configure_redis(configuration: Dict[str, Any], environ: Any, logger: Any, client_type: int = 1,
                    decode_responses: bool = False) -> RedisConfig:
    # Extract the client type as an integer: 1 for simple, 2 for advanced (default is 1)
    # Extract decode_responses flag (default False)
    redis_obj = None
    redis_url = configuration.get("_redis_host")
    if redis_url and redis_url not in {"REDIS_SERVER", "", " "}:

        redis_obj = RedisClientFactory.create(redis_url, environ, client_type, logger, decode_responses)
        if not redis_obj:
            logger.warning("Exception while initializing the redis")
            sys.exit(0)
    return RedisConfig(redis_obj=redis_obj)

import enum
import functools
import logging
import sys
import typing as t

import structlog
from asgi_correlation_id import correlation_id
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PciConcursosRegion(str, enum.Enum):
    TODOS = "*"
    NACIONAL = "NACIONAL"
    CE = "CEARÁ"
    SP = "SÃO PAULO"
    RJ = "RIO DE JANEIRO"
    MG = "MINAS GERAIS"
    ES = "ESPÍRITO SANTO"
    PR = "PARANÁ"
    SC = "SANTA CATARINA"
    DF = "DISTRITO FEDERAL"
    GO = "GOIÁS"
    MS = "MATO GROSSO DO SUL"
    MT = "MATO GROSSO"
    AM = "AMAZONAS"
    AC = "ACRE"
    PA = "PARÁ"
    RO = "RONDÔNIA"
    TO = "TOCANTINS"
    AL = "ALAGOAS"
    BA = "BAHIA"
    MA = "MARANHÃO"
    PB = "PARAÍBA"
    PE = "PERNAMBUCO"
    PI = "PIAUÍ"
    RN = "RIO GRANDE DO NORTE"
    SE = "SERGIPE"
    SUDESTE = "REGIÃO SUDESTE"


REGION_CONFIG_MAP: dict[PciConcursosRegion, dict[str, str]] = {
    PciConcursosRegion.NACIONAL: {"start": "<h2>NACIONAL</h2>", "end": "<h2>REGIÃO SUDESTE</h2>"},
    PciConcursosRegion.CE: {"start": '<div class="uf">CEARÁ</div>', "end": '<div class="uf">MARANHÃO</div>'},
    PciConcursosRegion.SP: {"start": '<div class="uf">SÃO PAULO</div>', "end": '<div class="uf">RIO DE JANEIRO</div>'},
    PciConcursosRegion.RJ: {
        "start": '<div class="uf">RIO DE JANEIRO</div>',
        "end": '<div class="uf">MINAS GERAIS</div>',
    },
    PciConcursosRegion.MG: {
        "start": '<div class="uf">MINAS GERAIS</div>',
        "end": '<div class="uf">ESPÍRITO SANTO</div>',
    },
    PciConcursosRegion.ES: {"start": '<div class="uf">ESPÍRITO SANTO</div>', "end": "<h2>REGIÃO SUL</h2>"},
    PciConcursosRegion.PR: {"start": '<div class="uf">PARANÁ</div>', "end": '<div class="uf">RIO GRANDE DO SUL</div>'},
    PciConcursosRegion.SC: {"start": '<div class="uf">SANTA CATARINA</div>', "end": "<h2>REGIÃO CENTRO-OESTE</h2>"},
    PciConcursosRegion.DF: {"start": '<div class="uf">DISTRITO FEDERAL</div>', "end": '<div class="uf">GOIÁS</div>'},
    PciConcursosRegion.GO: {"start": '<div class="uf">GOIÁS</div>', "end": '<div class="uf">MATO GROSSO DO SUL</div>'},
    PciConcursosRegion.MS: {
        "start": '<div class="uf">MATO GROSSO DO SUL</div>',
        "end": '<div class="uf">MATO GROSSO</div>',
    },
    PciConcursosRegion.MT: {"start": '<div class="uf">MATO GROSSO</div>', "end": "<h2>REGIÃO NORTE</h2>"},
    PciConcursosRegion.AM: {"start": '<div class="uf">AMAZONAS</div>', "end": '<div class="uf">ACRE</div>'},
    PciConcursosRegion.AC: {"start": '<div class="uf">ACRE</div>', "end": '<div class="uf">PARÁ</div>'},
    PciConcursosRegion.PA: {"start": '<div class="uf">PARÁ</div>', "end": '<div class="uf">RONDÔNIA</div>'},
    PciConcursosRegion.RO: {"start": '<div class="uf">RONDÔNIA</div>', "end": '<div class="uf">TOCANTINS</div>'},
    PciConcursosRegion.TO: {"start": '<div class="uf">TOCANTINS</div>', "end": "<h2>REGIÃO NORDESTE</h2>"},
    PciConcursosRegion.AL: {"start": '<div class="uf">ALAGOAS</div>', "end": '<div class="uf">BAHIA</div>'},
    PciConcursosRegion.BA: {"start": '<div class="uf">BAHIA</div>', "end": '<div class="uf">CEARÁ</div>'},
    PciConcursosRegion.MA: {"start": '<div class="uf">MARANHÃO</div>', "end": '<div class="uf">PARAÍBA</div>'},
    PciConcursosRegion.PB: {"start": '<div class="uf">PARAÍBA</div>', "end": '<div class="uf">PERNAMBUCO</div>'},
    PciConcursosRegion.PE: {"start": '<div class="uf">PERNAMBUCO</div>', "end": '<div class="uf">PIAUÍ</div>'},
    PciConcursosRegion.PI: {"start": '<div class="uf">PIAUÍ</div>', "end": '<div class="uf">RIO GRANDE DO NORTE</div>'},
    PciConcursosRegion.RN: {
        "start": '<div class="uf">RIO GRANDE DO NORTE</div>',
        "end": '<div class="uf">SERGIPE</div>',
    },
    PciConcursosRegion.SE: {
        "start": '<div class="uf">SERGIPE</div>',
        "end": '<p style="text-align:center; margin:0; padding:10px 0 0 0; font-weight:bold; color:#205c98;">VISITE PERIODICAMENTE - ATUALIZAÇÃO DIÁRIA!!!</p>',
    },
}


class PciConcursosConfig(BaseModel):
    link: str = "https://www.pciconcursos.com.br/concursos/"
    region_config: dict[PciConcursosRegion, dict[str, str]] = REGION_CONFIG_MAP

    model_config = SettingsConfigDict(arbitrary_types_allowed=True)


class LoggingConfig(BaseModel):
    level: LoggingLevel = Field(description="Logging level for the application")
    format: t.Literal["JSON", "PLAIN"] = Field(
        description="Logging output format - JSON for structured logs or PLAIN for console"
    )
    model_config = SettingsConfigDict(
        frozen=True,
    )


class Settings(BaseSettings):
    # NOTE: Application: service settings
    host: str = Field(description="Host address to bind the server to")
    port: int = Field(description="Port number to run the server on")
    workers: int = Field(default=1, description="Number of worker processes")
    logging: LoggingConfig = Field(description="Logging configuration settings")
    app_version: str = Field(default="0.1.0", description="Application version", min_length=1)
    git_commit_sha: str = Field(default="sha", description="Git commit SHA", min_length=1)

    # NOTE: Infrastructure: SQL database settings
    db_host: str = Field(default="db", description="Address to the SQL database host")
    db_port: str = Field(default="5432", description="Port number to connect to the SQL database")
    db_name: str = Field(default="concursos", description="SQL Database name")
    db_user: str = Field(default="app", description="User with proper permission to the SQL database")
    db_password: str = Field(default="secret", description="Password credential to the SQL database")

    # NOTE: Infrastructure: Cache Settings
    cache_host: str = Field(default="cache_default", description="Address to cache DB host")
    cache_port: str = Field(default="6379", description="Port for cache DB connection")
    cache_user: str = Field(default="default", description="User for cache DB authentication")
    cache_password: str = Field(default="default", description="Password for cache DB authentication")
    cache_name: str = Field(default="concursos", description="Password for cache DB authentication")

    model_config = SettingsConfigDict(
        env_file=(".env.default", ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
        frozen=True,
    )


def add_correlation_id(_, __, event_dict):
    cid = correlation_id.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def add_application_version(app_version: str, _, __, event_dict):
    event_dict["version"] = app_version
    return event_dict


def add_git_commit(git_commit: str, _, __, event_dict):
    event_dict["git_commit"] = git_commit
    return event_dict


def configure_structlog(app_version: str, git_commit: str, config: LoggingConfig) -> None:
    log_level = logging._nameToLevel.get(config.level)
    if log_level is None:
        raise ValueError(f"Invalid logging level: {config.level}")

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            add_correlation_id,
            functools.partial(add_application_version, app_version),
            functools.partial(add_git_commit, git_commit),
            structlog.processors.EventRenamer(to="message"),
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog's ProcessorFormatter
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    pre_chain = [
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer()
            if config.format == "JSON"
            else structlog.dev.ConsoleRenderer(event_key="message"),
        ],
        foreign_pre_chain=pre_chain,  # type: ignore[arg-type]
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)


def create_std_logging_config(app_version: str, git_commit: str, config: LoggingConfig) -> dict[str, t.Any]:
    """Logging configuration for uvicorn using standard logging module.

    The main goal is to render the logs the same way as structlog does.

    See:
        https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
    """
    # For verbose loggers, use the maximum of WARNING or user's configured level
    # This ensures they're at least WARNING but respects higher levels like ERROR
    user_level = logging._nameToLevel.get(config.level.value, logging.INFO)
    verbose_logger_level = logging.getLevelName(max(logging.WARNING, user_level))

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "foreign_pre_chain": [
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.stdlib.add_log_level,
                    structlog.processors.StackInfoRenderer(),
                ],
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    add_correlation_id,
                    functools.partial(add_application_version, app_version),
                    functools.partial(add_git_commit, git_commit),
                    structlog.processors.EventRenamer(to="message"),
                    structlog.processors.JSONRenderer()
                    if config.format == "JSON"
                    else structlog.dev.ConsoleRenderer(event_key="message"),
                ],
            },
        },
        "handlers": {
            "structlog": {
                "formatter": "structlog",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["structlog"],
                "level": config.level.value,
                "propagate": False,
            },
            "uvicorn.error": {"level": config.level.value},
            "uvicorn.access": {
                "handlers": ["structlog"],
                "level": config.level.value,
                "propagate": False,
            },
            # These are verbose loggers - set to minimum WARNING but respect higher user levels
            "httpx": {
                "handlers": ["structlog"],
                "level": verbose_logger_level,
                "propagate": False,
            },
            "httpcore": {
                "handlers": ["structlog"],
                "level": verbose_logger_level,
                "propagate": False,
            },
        },
    }

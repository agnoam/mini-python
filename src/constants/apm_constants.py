from enum import Enum
from typing import Final

class DecoratorType(Enum):
    Transaction: Final[int] = 1
    Span: Final[int] = 2

class DefaultValues:
    APM_SERVICE_NAME: Final[str] = 'python_service'
    APM_SERVER_URL: Final[str] = 'http://localhost:8200'
    APM_ENVIRONMENT: Final[str] = 'Development'

class TransactionTypes(Enum):
    DEFAULT: Final[str] = 'default'
    BOOT_LOOP: Final[str] = 'boot_loop'
    BACKGROUND_PROCESS: Final[str] = 'background_process'
    QUEUE_HANDLER: Final[str] = 'queue_handler'

class SpanTypes:
    TASK: Final[str] = 'task'
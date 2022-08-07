import os
from typing import Any
from functools import wraps
from typing import Callable

import elasticapm
from elasticapm.base import Client
from elasticapm.traces import Span, Transaction, TraceParent

from constants.apm_constants import DefaultValues, SpanTypes, TransactionTypes

# from dotenv import load_dotenv
# load_dotenv() # Take environment variables from .env

# TODO: Create decorator for tracking a transaction and span
apm: Client = elasticapm.Client(
    service_name = os.getenv('APM_SERVICE_NAME', DefaultValues.APM_SERVICE_NAME),
    server_url = os.getenv('APM_SERVER_URL', DefaultValues.APM_SERVER_URL),
    environment = os.getenv('APM_ENVIRONMENT', DefaultValues.APM_ENVIRONMENT)
)

# Automatically instrumenting app's http requests, database queries, etc.
elasticapm.instrument()

def create_transaction(
    name: str, 
    type: TransactionTypes = TransactionTypes.DEFAULT, 
    trace_parent: TraceParent = None

) -> Transaction:
    transaction: Transaction = apm.begin_transaction(type.name, trace_parent)
    transaction.name = name
    return transaction

# The name of the function is the name of the decorator ("decorator factory")
def trace_function(
    transaction: Transaction = None, 
    span_type: SpanTypes | None = None, 
    span_name: str | None = None
) -> None:
    def trace_decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _transaction: Transaction = transaction

            try:
                if not _transaction:
                    _transaction: Transaction = kwargs['transaction']
                    
                    # Removing the transaction kwarg, just in case the function does not use it at all
                    if not 'transaction' in func.__code__.co_varnames:
                        kwargs.pop('transaction', None)
                
                if not _transaction:
                    raise Exception(f'Can not trace {func.__name__} function without a transaction')
            except Exception as ex:
                raise Exception(ex)

            span: Span = _transaction.begin_span(span_name or func.__name__, span_type)
            res = func(*args, **kwargs)
            span.end()

            return res
        return wrapper
    return trace_decorator
from typing import Any

from elasticapm.traces import Span, Transaction
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from configs.apm_config import apm, create_transaction, trace_function
from constants.apm_constants import TransactionTypes

@trace_function(transaction=create_transaction('Receive docx file', TransactionTypes.QUEUE_HANDLER))
def receive_docx_handler(
    channel: Channel, method: Basic.Deliver,
    properties: BasicProperties, body: Any
) -> None:
    # try:
    print('Received a message', {
        'channel': channel, 
        'method': method, 
        'properties': properties,
        'body': body
    })
    # except Exception as ex:
    #     apm.capture_exception(ex)
    #     print(f'Caught rabbitmq_callback exception: {ex}', 'red')
    pass
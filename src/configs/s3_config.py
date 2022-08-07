from __future__ import annotations
import os
from typing import Any

import boto3
from boto3_type_annotations.s3 import Client

from configs.apm_config import trace_function
from constants.apm_constants import SpanTypes
from constants.s3_constants import EnvKeys

# from src.constants.constants import AWS_ACCESS_KEY_ID_ENV_KEY, AWS_SECRET_ACCESS_KEY_ENV_KEY, AWS_URI_ENV_KEY

# TODO: Change with etcd
# from dotenv import load_dotenv
# load_dotenv() # Take environment variables from .env

class S3Config:
    S3: Client = None

    @staticmethod
    @trace_function(span_name="S3 initialization", span_type=SpanTypes.TASK)
    def initialize_s3(uri: str = None, access_key_id: str = None, secret_access_key: str = None) -> None:
        """
            Initialize S3 connection - Creating the client object that communicates with the S3
        """
        if S3Config.S3 is None: 
            if uri is None:
                uri = str(os.getenv(EnvKeys.AWS_URI))

            if access_key_id is None:
                access_key_id = str(os.getenv(EnvKeys.AWS_ACCESS_KEY_ID))

            if secret_access_key is None:
                secret_access_key = str(os.getenv(EnvKeys.AWS_SECRET_ACCESS_KEY))

            S3Config.S3 = boto3.client(
                's3',
                aws_access_key_id = access_key_id,
                aws_secret_access_key = secret_access_key,
                endpoint_url = uri
            )

class S3Path:
    def __init__(self, bucket: str, key: str, https: bool = False, host: str = 'localhost', port: int = 4569) -> None:
        self.bucket = bucket
        self.key = key
        self.https = https
        self.host = host
        self.port = port

    @staticmethod
    def from_dict(dict: dict[str, Any]) -> S3Path:
        """
            Create S3Path object from dictionary

            returns `S3Path` object
        """
        default_dict: dict[str, Any] = {
            'Bucket': '',
            'Key': '',
            'Https': False,
            'Host': 'localhost',
            'Port': 4569
        }

        dict_to_create: dict[str, Any] = { **default_dict, **dict }

        if (dict_to_create['Bucket'] == '' or dict_to_create['Bucket'] == None or 
            dict_to_create['Key'] == '' or dict_to_create['Key'] == None):
            raise Exception("Argument must have a value for 'Bucket' and 'Key' properties")

        return S3Path(
            str(dict['Bucket']), 
            str(dict['Key']), 
            https=bool(dict['Https']) or False, 
            host=str(dict['Host']) or 'localhost', 
            port=int(dict['Port']) or 4569
        )

    def to_dict(self) -> dict[str, str]:
        """
            Extracts the `bucket` and `key` properties from the S3Path object
            returns: `dictionary` - With the data of the S3Path object
        """
        return {
            'Bucket': self.bucket,
            'Key': self.key,
            'Https': self.https,
            'Host': self.host,
            'Port': self.port
        }

    def to_url(self) -> str:
        """
            Generates a URL from the S3Path object
            
            returns: `string` - contains the URL
        """
        protocol: str = 'http'
        protocol = 'https' if self.https else protocol
        
        return f'{protocol}://{self.host}:{self.port}/{self.bucket}/{self.key}'
import os

from dotenv import load_dotenv
from flask import Flask

from app import caching
from app.secret_keys import *
from app.utils.aws_utils import create_polly_client, create_s3_client
from app.utils.openai_utils import create_openai_client

load_dotenv()

app = Flask(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = caching.create_redis_client(REDIS_HOST, REDIS_PORT)
s3_client = create_s3_client(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)
polly_client = create_polly_client(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("SHUO_TTS_BUCKET_REGION"),
)
openai_client = create_openai_client(openai_api_key=os.environ.get("OPENAI_API_KEY"))

from app.api.test_views import *
from app.api.views import *

if __name__ == "__main__":
    app.run()

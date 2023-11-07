from flask import Flask

from app import caching
from app.secret_keys import *
from app.tts.aws_polly import create_polly_client

app = Flask(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = caching.create_redis_client(REDIS_HOST, REDIS_PORT)
polly_client = create_polly_client(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)

test_tts_object = "tts.e0a6a1b2-e739-4c00-853d-67febd415da2.mp3"

from app.api.test_views import *
from app.api.views import *

if __name__ == "__main__":
    app.run()

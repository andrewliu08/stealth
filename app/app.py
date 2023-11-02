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
test_tts_presigned_url = "https://shuopolly.s3.amazonaws.com/tts.e6c28328-bcf6-4652-aeea-98be32107716.mp3?AWSAccessKeyId=AKIAUAUBZVHG5XLUVMHO&Signature=4MfXoYlaIw0uRUwU5i5rLrgns7M%3D&Expires=1698615813"

from app.api.views import *

if __name__ == "__main__":
    app.run()

import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DB = os.getenv('NEO4J_DB')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

BOT_TOKEN = os.getenv('BOT_TOKEN')
TEMPLATE_IMAGE_FILENAME_SAVE = os.getenv('TEMPLATE_IMAGE_FILENAME_SAVE')
NODES_GROUP_NAME = os.getenv('NODES_GROUP_NAME')

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
TEMPLATE_IMAGE_FILENAME_GET = os.getenv('TEMPLATE_IMAGE_FILENAME_GET')
BUCKET_NAME = os.getenv('BUCKET_NAME')


from minio import Minio
import hashlib
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TEMPLATE_IMAGE_FILENAME_GET, BUCKET_NAME


try:
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    print("Connected to Minio")
    print("List of buckets = ", client.list_buckets())
except:
    print("Cannot connect to Minio")

def fileHash(filename:str):
    return hashlib.md5(open(filename,'rb').read()).hexdigest()

#todo: put used hashes into key-value db
def save_file(filename:str, bucket = BUCKET_NAME) -> str:
    file_extension = filename.split(".")[-1]
    filename_of_savedFile = fileHash(filename) + '.' + file_extension
    client.fput_object(bucket, filename_of_savedFile, filename)
    return filename_of_savedFile
    
def get_file(filename:str, bucket = BUCKET_NAME):
    client.fget_object(bucket, filename, TEMPLATE_IMAGE_FILENAME_GET)
    return TEMPLATE_IMAGE_FILENAME_GET




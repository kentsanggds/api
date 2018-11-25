import os

from flask import current_app

from google.auth import compute_engine
from google.cloud import storage


class Storage(object):

    def __init__(self, bucket_name):
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            credentials = compute_engine.Credentials()
            self.storage_client = storage.Client(credentials=credentials, project=os.environ['PROJECT'])
        else:
            self.storage_client = storage.Client()

        if bucket_name not in self.storage_client.list_buckets():
            self.bucket = self.storage_client.create_bucket(bucket_name)
            current_app.logger.info('Bucket {} created'.format(self.bucket.name))
        else:
            self.bucket = self.storage_client.get_bucket(bucket_name)

    def upload_blob(self, source_file_name, destination_blob_name, set_public=True):
        blob = self.bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        if set_public:
            blob.make_public()

        current_app.logger.info('File {} uploaded to {}.'.format(
            source_file_name,
            destination_blob_name))

    def blob_exists(self, prefix, delimiter=None):
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        return any(True for _ in blobs)
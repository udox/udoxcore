from backends.s3 import S3Storage

import time

class S3backend_timestamp(S3Storage):
    """Amazon Simple Storage Service"""
    def get_available_name(self, name):
        """ Never overwrite - give each file a timestamp. """
        return '%s_%s' % (time.time(), name)

class S3backend_overwrite(S3Storage):
    """Amazon Simple Storage Service"""
    def get_available_name(self, name):
        """ always overwrite files. """
        return name

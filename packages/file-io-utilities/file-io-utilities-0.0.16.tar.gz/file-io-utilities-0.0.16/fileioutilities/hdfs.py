import os
from hdfs import InsecureClient
from .file_io import FileIO
from alidaargparser import get_asset_property



class Hdfs(FileIO):

    storage_type = os.path.basename(__file__).split('.py')[0]
    
    def __init__(self, name=None):
        super().__init__()
        self.name = name
        self.web_hdfs_url = get_asset_property(asset_name=self.name, property='webHdfsUrl')

    def upload(self, local_path, remote_path=None):
        if remote_path is None:
            remote_path = self.get_remote_path()
        # Upload model to HDFS
        client = InsecureClient(self.web_hdfs_url)
        client.upload(remote_path, local_path, overwrite=True, temp_dir="/tmp")
        client.set_permission(remote_path, "777")

    def download(self, local_path, remote_path=None):
        if remote_path is None:
            remote_path = self.get_remote_path()
        # Dowload model from HDFS to disk
        client = InsecureClient(self.web_hdfs_url)
        client.download(remote_path, local_path, overwrite=True, temp_dir="/tmp")

    def get_modification_time(self):
        if path is None:
            path = self.get_remote_path()
        # Get time when last modified
        url = url = "http:" + self.web_hdfs_url.split(":")[1] + ":50070"
        client = InsecureClient(url)
        return client.status(hdfs_path=path)['modificationTime']

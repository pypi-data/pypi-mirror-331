from .get_arguments import get_argument
from .file_io import FileIO
from datetime import datetime

import requests
import os
import json


class Http(FileIO):

    storage_type = os.path.basename(__file__).split('.py')[0]

    def __init__(self, name=None) -> None:
        self.name=name

    def download(self, local_path, remote_path=None):
        if remote_path is None:
            remote_path = self.get_remote_path()

        headers = {}
        headers_from_env = os.getenv('HEADERS')
        if headers_from_env is not None:
            headers.update(json.loads(headers_from_env))

        get_response = requests.get(remote_path, stream=True, headers=headers)
        
        #original_file_name  = remote_path.split("/")[-1] # original name of the file. Ignored for now, but leave this for future needs
 
        with open(local_path, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    def upload(self, local_path, remote_path=None):
        raise NotImplementedError

    def get_modification_time(self):
        return datetime.now()

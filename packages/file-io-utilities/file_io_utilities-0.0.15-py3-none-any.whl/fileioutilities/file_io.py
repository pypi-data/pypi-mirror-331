from abc import ABC, abstractmethod
from alidaargparser import get_asset_property

class FileIO(ABC):

    def __new__(cls, *args, **kw):

        if 'name' in kw:
            # Get storage type from properties
            storage_type = get_asset_property(asset_name=kw['name'], property="storage_type")
            if storage_type is None:
                storage_type = "filesystem"
        elif len(args)>0:
            storage_type = get_asset_property(asset_name=args[0], property="storage_type")
        else:
            storage_type = "filesystem"

        # Create a map of all subclasses based on storage type property (present on each subclass)
        subclass_map = {subclass.storage_type: subclass for subclass in cls.__subclasses__()}

        # Select the proper subclass based on
        subclass = subclass_map[storage_type.lower()]
        instance = super(FileIO, subclass).__new__(subclass)
        return instance
    
    def __init__(self, name = None):
        super().__init__()
      
    @abstractmethod
    def upload(self, local_path, remote_path):
        pass

    @abstractmethod
    def download(self, remote_path, local_path):
        pass
    
    @abstractmethod
    def get_modification_time(self, path):
        pass

    def get_remote_path(self):
        return get_asset_property(asset_name=self.name)
import os
from .file_io import FileIO
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from distutils.file_util import copy_file
from alidaargparser import get_asset_property
import shutil
import os

def copy_item(source, destination):
    """
    Copies a file or folder from the source path to the destination path.

    :param source: Path to the source file or folder.
    :param destination: Path to the destination.
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"The source path '{source}' does not exist.")
    
    # Check if the source is a file or directory
    if os.path.isfile(source):
        # Copy the file to the destination
        shutil.copy2(source, destination)
        print(f"File '{source}' has been copied to '{destination}'.")
    elif os.path.isdir(source):
        if not os.path.exists(destination):
            # Copy the directory to the destination
            shutil.copytree(source, destination)
        print(f"Directory '{source}' has been copied to '{destination}'.")
    else:
        raise ValueError("The source path must be a file or a directory.")


class Filesystem(FileIO):

    storage_type = os.path.basename(__file__).split('.py')[0]
    
    def __init__(self, name=None):
        super().__init__()
        self.name=name

    def upload(self, local_path, remote_path=None):
        if remote_path is None:
            remote_path = self.get_remote_path()

        copy_item(local_path, remote_path)
        print("Faking upload because it's running locally.")

    def download(self, local_path, remote_path=None):
        if remote_path is None:
            remote_path = self.get_remote_path()

        copy_item(remote_path, local_path)
        print("Faking download because it's running locally.")
        
    def get_modification_time(self):
        path = self.get_remote_path()
        return os.path.getmtime(path)


    # def copy_tree_or_file(self, from_path, to_path):
    #     if not os.path.exists(from_path):
    #         raise Exception("File or folder not present! Be sure that you're saving your file (model?) correctly.")
    #     # If it's a folder (compliant with older versions of python, now better ways are present).
    #     try:
    #         copy_tree(from_path, to_path)
    #     except DistutilsFileError:
    #         # If it's a file 
    #         copy_file(from_path, to_path)


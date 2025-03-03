import os
from typing import List
import logging

class UploadManager:
    """This is a builder style class, which will provide user with entry point into program.
    Abstract away entire underlying implementation."""

    def __init__(self):
        self.session_file: str = ""
        self.geometry_file: str = ""
        self.output_file: str = ""
        self.checkpoint_files: str = []
        self.filter_files: str = []

    def add_session_file(self,file_path: str) -> None:
        """Adds a session file path, resoliving to absolute path.

        Args:
            file_path (str): File path to session file, relative or absolute
        """
        try:
            abs_path = self._get_abs_path(file_path)
            self.session_file = abs_path
            logging.info(f"Session file set to: {abs_path} in {self.__class__.__name__}")
        except Exception as e:
            logging.error(f"Failed to add session file {file_path} in {self.__class__.__name__}: {e}")
            raise 

    def add_geometry_file(self,file_path: str) -> None:
        try:
            abs_path = self._get_abs_path(file_path)
            self.geometry_file = abs_path
            logging.info(f"Geometry file set to: {abs_path} in {self.__class__.__name__}")
        except Exception as e:
            logging.error(f"Failed to add geometry file {file_path} in {self.__class__.__name__}: {e}")
            raise 

    def add_output_file(self,file_path: str) -> None:
        try:
            abs_path = self._get_abs_path(file_path)
            self.output_file = abs_path
            logging.info(f"Output file set to: {abs_path} in {self.__class__.__name__}")
        except Exception as e:
            logging.error(f"Failed to add output file {file_path} in {self.__class__.__name__}: {e}")
            raise 

    def add_checkpoint_files(self,file_paths: List[str]) -> None:
        #TODO
        #need some info and error loggers here
        self.checkpoint_files = [self._get_abs_path(file) for file in file_paths]

    def add_filter_files(self,file_paths: List[str]) -> None:
        #TODO
        #need some info and error loggers here
        self.filter_files = [self._get_abs_path(file) for file in file_paths]
        
    def add_files_from_directory(self,dir_path: str) -> None:
        files = self._get_all_files_from_dir(dir_path)

        checkpoint_files: List[str] = []
        filter_files: List[str] = []
        for f in files:
            if self._has_extension(f,".xml"):
                self.add_session_file(f)
            elif self._has_extension(f,".fld"):
                self.add_output_file(f)
            elif self._has_extension(f,".nekg"):
                self.add_geometry_file(f)
            elif self._has_extension(f,".chk"):
                checkpoint_files.append(f)
            elif self._has_extension(f,".fce"):
                filter_files.append(f)
            else:
                msg = f"Ignoring unknown file {f} in directory {dir_path}"
                logging.info(msg)

        self.add_checkpoint_files(checkpoint_files)
        self.add_filter_files(filter_files)

    def _has_extension(self, file_path: str, extension: str) -> bool:
        """Check if the file has the given extension."""
        return file_path.lower().endswith(extension.lower())

    def _get_abs_path(self, rel_path: str) -> str:
        """Convert a relative file path to an absolute file path."""
        return os.path.abspath(rel_path)

    def _get_all_files_from_dir(self,dir_path: str) -> List[str]:
        try:
            abs_dir_path = self._get_abs_path(dir_path)
            files = [os.path.join(abs_dir_path, f) for f in os.listdir(abs_dir_path) if os.path.isfile(os.path.join(abs_dir_path, f))]
            logging.info(f"Found {len(files)} files in directory {abs_dir_path}")
            return files
        except Exception as e:
            logging.error(f"Failed to list files in directory {dir_path}: {e}")
            raise
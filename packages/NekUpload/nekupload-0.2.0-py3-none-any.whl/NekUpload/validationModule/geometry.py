import os
from  .hdf5schema_validator import GeometrySchemaHDF5Validator
import h5py
from .custom_exceptions import GeometryFileException

class ValidateGeometry:

    def __init__(self, file_path: str):
        self.file = file_path
        self.file_name = os.path.basename(self.file)

    def check_schema(self):
        """_summary_

        Raises:
            GeometryFileException: _description_

        Returns:
            _type_: _description_
        """
        try:
            with h5py.File(self.file, 'r') as f:
                self.schema_checker = GeometrySchemaHDF5Validator(f)
                self.schema_checker.validate()
        except OSError as e:
            raise GeometryFileException(self.file,f"Geometry file either does not exist or is not in HDF5 format {e}")

        return True        
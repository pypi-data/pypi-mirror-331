import os
import h5py
from .hdf5schema_validator import OutputSchemaHDF5Validator
from .custom_exceptions import OutputFileException

class ValidateOutput:
    def __init__(self, file_path: str):
        self.file = file_path
        self.file_name = os.path.basename(self.file)

    def check_schema(self):
        """Check Output file conforms to HDF5 schema

        Raises:
            OutputSchemaHDF5Validator: _description_

        Returns:
            _type_: _description_
        """
        try:
            with h5py.File(self.file, 'r') as f:
                self.schema_checker = OutputSchemaHDF5Validator(f)
                self.schema_checker.validate()
        except OSError as e:
            raise OutputFileException(self.file,f"Geometry file either does not exist or is not in HDF5 format {e}")

        return True
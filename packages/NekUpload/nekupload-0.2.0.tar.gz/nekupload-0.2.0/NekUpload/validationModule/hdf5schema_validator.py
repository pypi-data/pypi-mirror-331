from abc import ABC, abstractmethod
import h5py
from typing import List,Tuple,Set,Dict,Optional
from types import MappingProxyType
from .custom_exceptions import HDF5SchemaExistenceException,HDF5SchemaMissingDatasetException
from .custom_exceptions import HDF5SchemaInconsistentException,HDF5SchemaMissingDefinitionException,HDF5SchemaExtraDefinitionException
from dataclasses import dataclass,field
from NekUpload.utils import parsing

class HDF5Definition(ABC):
    @abstractmethod
    def validate(self,h5py_file: h5py.File):
        pass

@dataclass(frozen=True)
class HDF5GroupDefinition(HDF5Definition):
    """Given an HDF5 file, responsible for checking group conforms to correct structure and contains
    the specified attributes. This is not an exclusive check, other non-specified attributes can also be present.
    All exceptions raised from this class are of type HDF5SchemaException or its children.

    Args:
        HDF5Definition (_type_): _description_
    """
    path: str
    attributes: List[str] = field(default_factory=list)

    def validate(self,f: h5py.File) -> bool:
        """_summary_

        Args:
            f (h5py.File): _description_

        Raises:
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_

        Returns:
            bool: _description_
        """
        if self.path not in f:
            raise HDF5SchemaExistenceException(f,f"HDF5 schema error, {self.path} is not in file")
        
        group: h5py.Group = f[self.path]
        if not isinstance(group, h5py.Group): 
            raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} is a {type(group)},not a group")

        #check attributes exist
        if not set(self.attributes).issubset(group.attrs.keys()):
            missing_attributes = set(self.attributes) - set(group.attrs.keys())
            if missing_attributes:
                raise HDF5SchemaInconsistentException(f, f"HDF5 schema error, missing attributes in {self.path}: {missing_attributes}")
    
        return True

    def __str__(self):
        return self.path

    def get_path(self):
        return self.path

@dataclass(frozen=True)
class HDF5DatasetDefinition(HDF5Definition):
    """Given an HDF5 file, responsible for checking if dataset conforms to schema expectations, such as shape constraints.
        All exceptions raised from this class are of type HDF5SchemaException or its children.

    Args:
        HDF5GroupDefinition (_type_): _description_
    """
    path: str
    dataset_shape: Tuple[int,...] = ()

    def validate(self, f: h5py.File) -> bool:
        """_summary_

        Args:
            f (h5py.File): _description_

        Raises:
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_
            HDF5SchemaException: _description_

        Returns:
            bool: _description_
        """
        if self.path not in f:
            raise HDF5SchemaExistenceException(f,f"HDF5 schema error, {self.path} is not in file")
        
        dataset: h5py.Dataset = f[self.path]
        if not isinstance(dataset,h5py.Dataset):
            raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} is a {type(dataset)}, not a dataset")
        
        #check dataset shape if it exists
        if self.dataset_shape:
            actual_shape: Tuple[int,...] = dataset.shape
            
            #check expected dimension
            if len(actual_shape) != len(self.dataset_shape):
                raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} has dataset shape {actual_shape}, but expecting {self.dataset_shape}")
            
            for size,constrained_size in zip(actual_shape,self.dataset_shape):
                # negatives denotes no size restriction on dataset shape
                #so only positive ones are constraints
                if constrained_size >= 0 and constrained_size != size:
                    raise HDF5SchemaInconsistentException(f,f"HDF5 schema error, {self.path} has dataset shape {actual_shape}, but expecting {self.dataset_shape}")
                
        return True
    
    def __str__(self):
        return self.path

    def get_path(self):
        return self.path

class GeometrySchemaHDF5Validator:
    NO_DIM_CONSTRAINTS = -1 #helper

    #TODO make these dict immutable
    #using immutable dictionary to define what structure of each group and dataset should look like regardless of geometry file
    #dict to help associate each set with a useful descriptor, which will be beneficial later on
    BASE_GROUPS: MappingProxyType[str,HDF5GroupDefinition] = MappingProxyType({"NEKTAR": HDF5GroupDefinition("NEKTAR"),
                                            "GEOMETRY": HDF5GroupDefinition("NEKTAR/GEOMETRY",attributes=["FORMAT_VERSION"]),
                                            "MAPS": HDF5GroupDefinition("NEKTAR/GEOMETRY/MAPS"),
                                            "MESH": HDF5GroupDefinition("NEKTAR/GEOMETRY/MESH")})

    DATASETS_MANDATORY_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                            {"VERT": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/VERT",(NO_DIM_CONSTRAINTS,)),
                                                            "DOMAIN": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/DOMAIN",(NO_DIM_CONSTRAINTS,)),
                                                            "COMPOSITE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/COMPOSITE",(NO_DIM_CONSTRAINTS,))
                                                            })

    DATASETS_MANDATORY_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                                {"CURVE_NODES": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/CURVE_NODES",(NO_DIM_CONSTRAINTS,3)),
                                                                "VERT": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/VERT",(NO_DIM_CONSTRAINTS,3)),
                                                                "DOMAIN": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/DOMAIN",(NO_DIM_CONSTRAINTS,)),
                                                                "COMPOSITE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/COMPOSITE",(NO_DIM_CONSTRAINTS,))
                                                                })
    
    DATASETS_1D_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"SEG": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/SEG",(NO_DIM_CONSTRAINTS,)),
                                                        "CURVE_EDGE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/CURVE_EDGE",(NO_DIM_CONSTRAINTS,))
                                                        })
    
    DATASETS_1D_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"SEG": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/SEG",(NO_DIM_CONSTRAINTS,2)),
                                                        "CURVE_EDGE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/CURVE_EDGE",(NO_DIM_CONSTRAINTS,3))
                                                        })

    DATASETS_2D_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"TRI": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/TRI",(NO_DIM_CONSTRAINTS,)),
                                                        "QUAD": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/QUAD",(NO_DIM_CONSTRAINTS,)),
                                                        "CURVE_FACE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/CURVE_FACE",(NO_DIM_CONSTRAINTS,))
                                                        })
    
    DATASETS_2D_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"TRI": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/TRI",(NO_DIM_CONSTRAINTS,3)),
                                                        "QUAD": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/QUAD",(NO_DIM_CONSTRAINTS,4)),
                                                        "CURVE_FACE": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/CURVE_FACE",(NO_DIM_CONSTRAINTS,3))
                                                        })

    DATASETS_3D_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"HEX": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/HEX",(NO_DIM_CONSTRAINTS,)),
                                                        "TET": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/TET",(NO_DIM_CONSTRAINTS,)),
                                                        "PYR": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/PYR",(NO_DIM_CONSTRAINTS,)),
                                                        "PRISM": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MAPS/PRISM",(NO_DIM_CONSTRAINTS,))
                                                        })

    DATASETS_3D_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType(
                                                        {"HEX": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/HEX",(NO_DIM_CONSTRAINTS,6)),
                                                        "TET": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/TET",(NO_DIM_CONSTRAINTS,4)),
                                                        "PYR": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/PYR",(NO_DIM_CONSTRAINTS,5)),
                                                        "PRISM": HDF5DatasetDefinition("NEKTAR/GEOMETRY/MESH/PRISM",(NO_DIM_CONSTRAINTS,5))
                                                        })
    
    DATASETS_MAPS: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType({**DATASETS_MANDATORY_MAPS,**DATASETS_1D_MAPS,
                                                                                   **DATASETS_2D_MAPS,**DATASETS_3D_MAPS})

    DATASETS_MESH: MappingProxyType[str,HDF5DatasetDefinition] = MappingProxyType({**DATASETS_MANDATORY_MESH,**DATASETS_1D_MESH,
                                                                                   **DATASETS_2D_MESH,**DATASETS_3D_MESH})

    def __init__(self,f: h5py.File):        
        self.file: h5py.File = f

        self.datasets_present: Set[str] = set()
        self.element_number: Dict[str] = {}
        
    def validate(self) -> bool:
        #check mandatory groups
        for group in GeometrySchemaHDF5Validator.BASE_GROUPS.values():
            group.validate(self.file)
        
        #check all datasets
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_MANDATORY_MAPS))
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_MANDATORY_MESH))
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_1D_MAPS))
        self.datasets_present.update(self._check_mandatory_dataset(GeometrySchemaHDF5Validator.DATASETS_1D_MESH))

        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_2D_MAPS))
        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_2D_MESH))
        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_3D_MAPS))
        self.datasets_present.update(self._check_optional_dataset(GeometrySchemaHDF5Validator.DATASETS_3D_MESH))

        self._check_consistent_maps_mesh_definition(self.datasets_present,GeometrySchemaHDF5Validator.DATASETS_MAPS,GeometrySchemaHDF5Validator.DATASETS_MESH)

        self.element_number = self._get_number_of_elements(self.datasets_present,GeometrySchemaHDF5Validator.DATASETS_MESH)
        self._check_element_construction(self.element_number)

        #finally check no extra unexpected payload in file
        valid_groups_keys: List[str] = [group.get_path() for group in GeometrySchemaHDF5Validator.BASE_GROUPS.values()]
        self._check_only_valid_groups_exist(valid_groups_keys)

        valid_dataset_keys: List[str] = [dataset.get_path() for dataset in GeometrySchemaHDF5Validator.DATASETS_MESH.values()] + \
                                        [dataset.get_path() for dataset in GeometrySchemaHDF5Validator.DATASETS_MAPS.values()]
        self._check_only_valid_datasets_exist(valid_dataset_keys)

        return True
    
    def _check_only_valid_groups_exist(self,valid_groups: List[str]):
        """Check that only valid groups exist.

        Args:
            valid_groups (str): _description_
        """
        #plus one to search for any extra invalid groups
        #"" is a valid group too, and is provided in function call
        valid_groups.append("")
        max_groups = len(valid_groups) + 1 
        groups = parsing.get_hdf5_groups_with_depth_limit(self.file,3,max_groups=max_groups)

        for group in groups:
            if group not in valid_groups:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown group: {group}")

    def _check_only_valid_datasets_exist(self,valid_datasets: List[str]):
        """Check that only valid datasets exist.

        Args:
            valid_datasets (str): _description_
        """
        max_datasets = len(valid_datasets) + 1
        datasets = parsing.get_hdf5_datasets_with_depth_limit(self.file,3,max_datasets=max_datasets)
        for dataset in datasets:
            if dataset not in valid_datasets:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown dataset: {dataset}")

    def _check_mandatory_dataset(self,mandatory_datasets: MappingProxyType[str,HDF5DatasetDefinition]) -> Set[str]:
        """Helper function. Checks mandatory datasets and if all valid, return the keys of the present datasets

        Args:
            mandatory_datasets (MappingProxyType[str,HDF5DatasetDefinition]): Dictionary of datasets that should be present

        Returns:
            Set[str]: Set of keys denoting which datasets are present
        """
        datasets_present_key: Set[str] = set()

        for key,dataset in mandatory_datasets.items():
            if dataset.validate(self.file):
                datasets_present_key.add(key)

        return datasets_present_key


    def _check_optional_dataset(self,optional_dataset: MappingProxyType[str,HDF5DatasetDefinition]) -> Set[str]:
        """Helper function. Checks optional datasets and valid datasets will have their keys added to present datasets, which is returned.

        Args:
            optional_dataset (MappingProxyType[str,HDF5DatasetDefinition]): _description_

        Returns:
            Set[str]: Set of keys denoting which datasets are present

        Raises:
            HDF5SchemaException: _description_
        """
        datasets_present_key: Set[str] = set()

        for key,dataset in optional_dataset.items():
            try:
                dataset.validate(self.file)
                datasets_present_key.add(key)
            except HDF5SchemaExistenceException:
                pass #optional, so allow if doesn't exist, but any other definition error should be re-raised
            except Exception:
                raise

        return datasets_present_key

    def _check_consistent_maps_mesh_definition(self,
                                                present_datasets_keys: Set[str],
                                                dataset_maps: Dict[str,HDF5DatasetDefinition],
                                                dataset_mesh: Dict[str,HDF5DatasetDefinition]) -> None:
        """Check that for all present dataset keys, there is a consistent definition between the MAPS and MESH

        Args:
            present_datasets_keys (Set[str]): List of keys denoting datasets that are present
            dataset_maps (Set[str,HDF5DatasetDefinition]): _description_
            dataset_mesh (Dict[str,HDF5DatasetDefinition]): _description_
        """
        #now check that each pair exists and have consistent shapes
        #maps can't be defined without corresponding mesh and vice versa
        for key in present_datasets_keys:
            #curve nodes only exception to above rule
            if key != "CURVE_NODES":
                self._check_pair_of_datasets(dataset_maps.get(key),dataset_mesh.get(key))

    def _check_pair_of_datasets(self, dataset_map: HDF5DatasetDefinition, dataset_mesh: HDF5DatasetDefinition) -> None:
        """Helper funcion for checking whether a map and mesh dataset have consistent definitions

        Args:
            dataset_1 (HDF5DatasetDefinition): _description_
            dataset_2 (HDF5DatasetDefinition): _description_

        Raises:
            HDF5SchemaException: _description_
        """
        data_map = self.file.get(dataset_map.get_path())
        data_mesh = self.file.get(dataset_mesh.get_path())

        if (data_map is not None and data_mesh is None) or (data_mesh is not None and data_map is None):
            raise HDF5SchemaMissingDatasetException(self.file, f"HDF5 Schema Error: {dataset_map} and {dataset_mesh} should be defined together, \
                                                    but one exists and other doesn't")

        if data_map is not None and data_mesh is not None:
            if isinstance(data_map, h5py.Dataset) and isinstance(data_mesh, h5py.Dataset):
                shape_map = data_map.shape
                shape_mesh = data_mesh.shape
                if shape_map[0] != shape_mesh[0]:
                    raise HDF5SchemaInconsistentException(self.file, f"HDF5 Schema Error: {dataset_map} has shape {shape_map} and {dataset_mesh} \
                                                            has shape {shape_mesh}. Inconsistent lengths {shape_map[0]} != {shape_mesh[0]}")

    def _get_number_of_elements(self,
                                present_datasets_keys: Set[str],
                                dataset_mesh: Dict[str,HDF5DatasetDefinition]) -> Dict[str,int]:
        """For all datasets present in the geometry file, generate a dictionary mapping dataset keys to number of elements defined.
        Assumes consistency between maps and meshes, so meshes will be used as it contains CURVE_NODES

        Args:
            present_datasets_keys (Set[str]): _description_
            dataset_mesh (Dict[str,HDF5DatasetDefinition]): _description_

        Returns:
            Dict[str,int]: _description_
        """

        number_elements: Dict[str,int] = {}

        for dataset_key in present_datasets_keys:
            dataset_definition: HDF5DatasetDefinition = dataset_mesh[dataset_key]
            data = self.file.get(dataset_definition.get_path())
            shape = data.shape
            elmt_num = shape[0]
            number_elements[dataset_key] = elmt_num

        return number_elements

    def _check_element_construction(self,num_elements: Dict[str,int]):
        """Make sure element construction is consistent

        Args:
            num_elements (Dict[str,int]): _description_

        Raises:
            HDF5SchemaMissingDefinitionException: _description_
            HDF5SchemaMissingDefinitionException: _description_
            HDF5DatasetDefinition: _description_
        """
        #3D elements can only be defined if corresponding 2D elements are present
        quads = num_elements.get("QUAD",0)
        tris = num_elements.get("TRI",0)
        
        if num_elements.get("HEX",None) and quads < 6:
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: HEX requires quads. There are only {quads} QUADS defined")

        if num_elements.get("TET",None) and tris < 4:
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: TET requires tris. There are only {tris} TRIS defined")
            
        if num_elements.get("PYR",None) and (tris < 4 or quads < 1):
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: PYR requires quads and tris. There are only {tris} TRIS and {quads} QUADS defined")
        
        if num_elements.get("PRISM",None) and (tris < 2 or quads < 4):
            raise HDF5SchemaMissingDefinitionException(self.file,f"HDF5 Schema Error: PRISM requires quads and tris. There are only {tris} TRIS and {quads} QUADS defined")

class OutputSchemaHDF5Validator:

    NO_DIM_CONSTRAINTS = -1 #helper

    BASE_GROUPS = (HDF5GroupDefinition("NEKTAR",attributes=["FORMAT_VERSION"]),
                HDF5GroupDefinition("NEKTAR/Metadata",attributes=["ChkFileNum","Time"]), #this is bare minimum, depending on solver, can have more, also sessionFile#
                HDF5GroupDefinition("NEKTAR/Metadata/Provenance",attributes=["GitBranch","GitSHA1","Hostname","NektarVersion","Timestamp"]))

    EXPECTED_DATASETS = (HDF5DatasetDefinition("NEKTAR/DATA",(NO_DIM_CONSTRAINTS,)),
                        HDF5DatasetDefinition("NEKTAR/DECOMPOSITION",(NO_DIM_CONSTRAINTS,)),
                        HDF5DatasetDefinition("NEKTAR/ELEMENTIDS",(NO_DIM_CONSTRAINTS,)))

    def __init__(self,f: h5py.File):        
        self.file: h5py.File = f

    def validate(self):
        self._check_mandatory_groups(OutputSchemaHDF5Validator.BASE_GROUPS)
        self._check_mandatory_datasets(OutputSchemaHDF5Validator.EXPECTED_DATASETS)

        #acquire all other groups and datasets that should be present based on DECOMPOSITION definition
        self._assert_decomposition()
        expansion_groups: Tuple[HDF5GroupDefinition] = tuple(self._get_expansion_groups())
        optional_datasets: Tuple[HDF5DatasetDefinition] = tuple(self._get_optional_datasets())

        self._check_mandatory_groups(expansion_groups)
        self._check_mandatory_datasets(optional_datasets)
        
        #check no extraneous groups or datasets
        valid_groups: Tuple[HDF5GroupDefinition] = OutputSchemaHDF5Validator.BASE_GROUPS + expansion_groups
        valid_datasets: Tuple[HDF5DatasetDefinition] = OutputSchemaHDF5Validator.EXPECTED_DATASETS + optional_datasets

        valid_groups_str = [group.get_path() for group in valid_groups]
        valid_datasets_str = [dataset.get_path() for dataset in valid_datasets]
        self._check_only_valid_groups_exist(valid_groups_str)
        self._check_only_valid_datasets_exist(valid_datasets_str)

    def _check_mandatory_groups(self,groups: Tuple[HDF5GroupDefinition]):
        for group in groups:
            group.validate(self.file)

    def _check_mandatory_datasets(self,datasets: Tuple[HDF5DatasetDefinition]):
        for dataset in datasets:
            dataset.validate(self.file)

    def _assert_decomposition(self):
        """Assert decomposition has correct shape

        Raises:
            HDF5SchemaInconsistentException: _description_
        """
        #decomposition should come in group of 7
        if self.file["NEKTAR/DECOMPOSITION"].shape[0] % 7 != 0:
            raise HDF5SchemaInconsistentException(self.file,"HDF5 Schema Error: Decomposition shape should be multiple of 7")

    def _get_expansion_groups(self) -> List[HDF5GroupDefinition]:
        """Get the expansion groups that should be defined, based on what is in DECOMPOSITION

        Raises:
            HDF5SchemaInconsistentException: _description_

        Returns:
            List[HDF5GroupDefinition]: _description_
        """
        decomposition_dataset: h5py.Dataset = self.file["NEKTAR/DECOMPOSITION"]
        #last of the 7 is a hash pointing to location in HDF5 file containing expansion data
        num_expansion_groups = decomposition_dataset.shape[0] // 7

        expected_groups: List[HDF5GroupDefinition] = []
        for i in range(6,7*num_expansion_groups,7):
            hash = decomposition_dataset[i]
            expected_groups.append(HDF5GroupDefinition(f"NEKTAR/{hash}",attributes=["BASIS","FIELDS","NUMMODESPERDIR","SHAPE"]))

        return expected_groups
    
    def _get_optional_datasets(self) -> List[HDF5DatasetDefinition]:
        """Get all optional datasets defined by DECOMPOSITION

        Returns:
            List[HDF5DatasetDefinition]: _description_
        """
        optional_datasets: List[HDF5DatasetDefinition] = []

        optionals = {"NEKTAR/POLYORDERS": 2,
                    "NEKTAR/HOMOGENEOUSYIDS": 3,
                    "NEKTAR/HOMOGENEOUSZIDS": 4,
                    "NEKTAR/HOMOGENEOUSSIDS": 5}

        for name,idx in optionals.items():
            if dataset := self._get_dataset_defined_in_decomposition(name,idx):
                optional_datasets.append(dataset)

        return optional_datasets
    
    def _get_dataset_defined_in_decomposition(self,
                                            dataset_name: str,
                                            decomposition_entry_id: int) -> Optional[HDF5DatasetDefinition]:
        """DECOMPOSITION contains sequence of 7 entries, some of which will lead to definition of
        extra datasets within the file. When the following are non-zero, a dataset is expected, and
        are constructed with the same rule:

        Note starting from 0:
        2 -> number of modes when variable polynomial is defined
        3 -> number of y planes for homogeneous simulations
        4 -> number of z planes for homogeneous simulations
        5 -> number of strips for homogeneous simulations

        Args:
            dataset_name (str): Name of the dataset to be defined
            decomposition_entry_id (int): Decomposition entry id for desired dataset 

        Returns:
            Optional[HDF5DatasetDefinition]: Dataset schema definition if one is required
        """
        decomposition_dataset: h5py.Dataset = self.file["NEKTAR/DECOMPOSITION"]
        size = decomposition_dataset.shape[0]
        num_data_points: int = 0

        for i in range(decomposition_entry_id,size,7):
            num_data_points += decomposition_dataset[i]

        return HDF5DatasetDefinition(dataset_name,(num_data_points,)) if num_data_points > 0 else None

    def _get_polyorder_dataset(self) -> Optional[HDF5DatasetDefinition]:
        """Get the polyorder dataset definition if it should exist, based on DECOMPOSITION entries, every third entry

        Returns:
            Optional[HDF5DatasetDefinition]: _description_
        """
        decomposition_dataset: h5py.Dataset = self.file["NEKTAR/DECOMPOSITION"]
        size = decomposition_dataset.shape[0]
        #3rd of the 7 grouping in decomposition
        #is a number of modes that are polyorder???
        num_polyorder_modes: int = 0

        for i in range(2,size,7):
            num_polyorder_modes += decomposition_dataset[i]

        return HDF5DatasetDefinition("NEKTAR/POLYORDERS",(num_polyorder_modes,)) if num_polyorder_modes > 0 else None

    def _check_only_valid_groups_exist(self,valid_groups: List[str]):
        """Check that only valid groups exist.

        Args:
            valid_groups (str): _description_
        """
        #plus one to search for any extra invalid groups
        #"" is a valid group too, and is provided in function call
        valid_groups.append("")
        max_groups = len(valid_groups) + 1 
        groups = parsing.get_hdf5_groups_with_depth_limit(self.file,3,max_groups=max_groups)

        for group in groups:
            if group not in valid_groups:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown group: {group}")

    def _check_only_valid_datasets_exist(self,valid_datasets: List[str]):
        """Check that only valid datasets exist.

        Args:
            valid_datasets (str): _description_
        """
        max_datasets = len(valid_datasets) + 1
        datasets = parsing.get_hdf5_datasets_with_depth_limit(self.file,3,max_datasets=max_datasets)
        for dataset in datasets:
            if dataset not in valid_datasets:
                raise HDF5SchemaExtraDefinitionException(self.file,f"Encountered unkown dataset: {dataset}")

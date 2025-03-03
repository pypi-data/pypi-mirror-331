from lxml import etree
from .custom_exceptions import XMLSchemaException,MissingInputFileException,MissingOutputFileException
import os
from typing import List,Tuple,Dict
import logging
from NekUpload.utils import parsing

class ValidateSession:
    def __init__(self,file_path: str):
        self.file_path = file_path
        self.xml_tree = self._load_DOM_tree(self.file_path)

    def _load_DOM_tree(self, xml_file: str) -> etree._Element:
        with open(xml_file, "rb") as xml:
            xml_tree = etree.XML(xml.read())
        
        return xml_tree

    def is_valid_xml(self,xml_file: str,schema_file_path: str) -> bool:
        """_summary_

        Args:
            xml_file (str): _description_
            schema_file_path (str): _description_

        Raises:
            XMLSchemaException: _description_

        Returns:
            bool: _description_
        """
        xsd_file = schema_file_path
        
        with open(xsd_file,"rb") as xsd:
            schema_root = etree.XML(xsd.read())
            schema = etree.XMLSchema(schema_root)

        with open(xml_file,"rb") as xml:
            xml_tree = etree.XML(xml.read())
        
        if schema.validate(xml_tree):
            return True
        else:
            raise XMLSchemaException(self.file_path,schema.error_log)
    
    def check_schema(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        xsd_schema = os.path.join(os.path.dirname(__file__), 'schemas/nektar.xsd') #ensure path always correct
        return self.is_valid_xml(self.file_path, xsd_schema)
        
    def check_file_dependencies(self, files: List[str]) -> bool:
        
        #check geometry files exist
        geometry: etree._Element = self.xml_tree.find("GEOMETRY")
        expected_geometry_file = geometry.attrib.get("HDF5FILE")

        if expected_geometry_file not in files:
            raise MissingInputFileException(expected_geometry_file,"Geometry file is missing")
        
        #check correct number of checkpoint files
        conditions: etree._Element = self.xml_tree.find("CONDITIONS")
        params: etree._Element = conditions.find("PARAMETERS")

        #params has a bunch of p child elements, each with different 
        p_dict: Dict[str,str] = {}
        for p in params:
            content = p.text #containss an equals
            param_name,value = parsing.get_both_sides_of_equals(content)
            p_dict[param_name] = value

        #there is a possibility that it references other params, so store all in dict
        p_dict = parsing.evaluate_parameters(p_dict)

        num_steps = p_dict["NumSteps"]
        chk_steps = p_dict["IO_CheckSteps"]

        #at step=0, checkpoint file 0 is generated, hence +1
        num_chk_files = num_steps // chk_steps + 1

        chk_files = parsing.get_all_files_with_extension(files,".chk")

        if num_chk_files != len(chk_files):
            raise MissingOutputFileException(chk_files,
                                            f"There are {len(chk_files)}. Should have {num_chk_files}")

        return True
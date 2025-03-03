from abc import ABC,abstractmethod
from typing import Dict,Any,List
from .user import UserInfo

class Metadata:
    """_summary_
    """
    def __init__(self,title: str,publication_date:str,creators: List[UserInfo],resource_type):
        """_summary_

        Args:
            title (str): _description_
            publication_date (str): _description_
            creators (List[UserInfo]): _description_
            resource_type (_type_): _description_
        """
        pass

    @abstractmethod
    def get_metadata_payload(self) -> Dict[str,Any]:
        """_summary_

        Returns:
            Dict[str,Any]: _description_
        """
        pass

    @abstractmethod
    def add_version(self, version: str) -> None:
        """_summary_

        Args:
            version (str): _description_
        """
        pass

    @abstractmethod
    def add_description(self, description: str) -> None:
        """_summary_

        Args:
            description (str): _description_
        """
        pass

    @abstractmethod
    def add_publisher(self, publisher: str) -> None:
        """_summary_

        Args:
            publisher (str): _description_
        """
        pass

    @abstractmethod
    def to_json_serialisable(self) -> Dict[str,Any]:
        """_summary_

        Returns:
            Dict[str,Any]: _description_
        """
        pass

    @classmethod
    @abstractmethod
    def from_json(cls,data: Dict[str,Any]) -> 'Metadata':
        """_summary_

        Args:
            data (Dict[str,Any]): _description_

        Returns:
            Metadata: _description_
        """
        pass
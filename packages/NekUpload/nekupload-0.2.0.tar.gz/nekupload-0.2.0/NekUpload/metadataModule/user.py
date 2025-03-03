from abc import ABC,abstractmethod
from typing import Dict,Any,List,Set,Union
import logging
from .identifier import Identifier,IdentifierType

class UserInfo(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """
    @abstractmethod
    def get_info(self) -> Dict[str,Any]:
        """_summary_

        Returns:
            Dict[str,Any]: _description_
        """
        pass

    @abstractmethod
    def to_json_serialisable(self) -> Dict[str,Any]:
        pass

    @classmethod
    @abstractmethod
    def from_json(cls,data: Dict[str,Any]) -> Union['InvenioOrgInfo','InvenioPersonInfo']:
        """Factory method for deserialising. 

        Args:
            data (Dict[str,Any]): _description_

        Returns:
            UserInfo: _description_
        """
        if data["type"] == "personal":
            return  InvenioPersonInfo.from_json(data)
        elif data["type"] == "organizational":
            return InvenioOrgInfo.from_json(data)

    @abstractmethod
    def __eq__(self,other: 'UserInfo') -> bool:
        pass

class InvenioPersonInfo(UserInfo):
    """_summary_

    Args:
        UserInfo (_type_): _description_
    """
    def __init__(self, given_name: str, family_name: str) -> None:
        """_summary_

        Args:
            given_name (str): _description_
            family_name (str): _description_

        Raises:
            TypeError: _description_
        """

        if not isinstance(given_name, str) or not isinstance(family_name, str):
            msg = "Given name and family name must be strings."
            logging.error(msg)
            raise TypeError(msg)
        
        self.id_schemes: Set[IdentifierType] = set()

        self.type: str = "personal"
        self.given_name: str = given_name
        self.family_name: str = family_name
        self.identifiers: List[Identifier] = []

    def add_identifier(self,identifier: Identifier) -> None:
        """_summary_

        Args:
            identifier (Identifier): _description_

        Raises:
            ValueError: _description_
        """
        id_type: IdentifierType = identifier.get_id_type()
        
        if id_type in self.id_schemes:
            raise ValueError(f"Cannot have duplicate identifiers of same type for one organisation {id_type}")        

        self.id_schemes.add(id_type)
        self.identifiers.append(identifier)

    def get_info(self) -> Dict[str,Any]:
        """_summary_

        Returns:
            Dict[str,Any]: _description_
        """

        identifier_payload = []
        for identifier in self.identifiers:
            payload = {
                "scheme": identifier.get_id_type().value.lower(),
                "identifier": identifier.get_id()
            }
            identifier_payload.append(payload)

        data = {
            "type": self.type,
            "given_name": self.given_name,
            "family_name": self.family_name,
        }

        if identifier_payload != []:
            data["identifiers"] = identifier_payload 

        return data
    
    def __str__(self):
        return f"Person: {self.given_name} {self.family_name}"

    def to_json_serialisable(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        data = {
            "type": self.type,
            "given_name": self.given_name,
            "family_name": self.family_name,
        }

        #do not add empty fields
        identifiers = [id.to_json_serialisable() for id in self.identifiers]
        if identifiers != []:
            data["identifiers"] = identifiers

        return data
    
    @classmethod
    def from_json(cls,data: Dict[str,Any]) -> 'InvenioPersonInfo':
        """_summary_

        Args:
            data (Dict[str,Any]): _description_

        Returns:
            InvenioPersonInfo: _description_
        """
        given_name = data["given_name"]
        family_name = data["family_name"]

        data_identifiers = data.get("identifiers",[])#in case not present in dict
        identifiers: List[Identifier] = [Identifier.from_json(id) for id in data_identifiers]
        
        person = InvenioPersonInfo(given_name,family_name)

        for identifier in identifiers:
            person.add_identifier(identifier)

        return person

    def __eq__(self,other: 'InvenioPersonInfo') -> bool:
        if not isinstance(other, InvenioPersonInfo):
            return False
        
        return (
            self.type == other.type and
            self.given_name == other.given_name and
            self.family_name == other.family_name and
            self.identifiers == other.identifiers
        )

class InvenioOrgInfo(UserInfo):
    """_summary_

    Args:
        UserInfo (_type_): _description_
    """
    def __init__(self, name: str) -> None:
        """_summary_

        Args:
            name (str): _description_
        """
        self.id_schemes: Set[IdentifierType] = set()
        self.type: str = "organizational"
        self.name: str = name
        self.identifiers: List[Identifier] = []

    def get_info(self) -> Dict[str,Any]:
        """_summary_

        Returns:
            Dict[str,Any]: _description_
        """

        identifier_payload = []
        for identifier in self.identifiers:
            payload = {
                "scheme": identifier.get_id_type().value.lower(),
                "identifier": identifier.get_id()
            }
            identifier_payload.append(payload)

        data = {
            "type": self.type,
            "name": self.name,
        }

        if identifier_payload != []:
            data["identifiers"] = identifier_payload 

        return data
    
    def add_identifier(self,identifier: Identifier) -> None:
        """_summary_

        Args:
            identifier (Identifier): _description_

        Raises:
            ValueError: _description_
        """
        id_type: IdentifierType = identifier.get_id_type()
        
        if id_type in self.id_schemes:
            raise ValueError(f"Cannot have duplicate identifiers of same type for one organisation {id_type}")        

        self.id_schemes.add(id_type)
        self.identifiers.append(identifier)

    def __str__(self):
        return f"Organisation: {self.name}"
    
    def to_json_serialisable(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        data = {
            "type": self.type,
            "name": self.name,
        }

        #do not add empty fields
        identifiers = [id.to_json_serialisable() for id in self.identifiers]
        if identifiers != []:
            data["identifiers"] = identifiers

        return data
    
    @classmethod
    def from_json(cls,data: Dict[str,Any]) -> 'InvenioOrgInfo':
        """_summary_

        Args:
            data (Dict[str,Any]): _description_

        Returns:
            InvenioOrgInfo: _description_
        """
        name = data["name"]

        data_identifiers = data.get("identifiers",[])#in case not present in dict
        identifiers: List[Identifier] = [Identifier.from_json(id) for id in data_identifiers]
        
        org = InvenioOrgInfo(name)

        for identifier in identifiers:
            org.add_identifier(identifier)

        return org
    
    def __eq__(self,other: 'InvenioOrgInfo') -> bool:
        if not isinstance(other, InvenioOrgInfo):
            return False
        
        return (
            self.type == other.type and
            self.name == other.name and
            self.identifiers == other.identifiers
        )
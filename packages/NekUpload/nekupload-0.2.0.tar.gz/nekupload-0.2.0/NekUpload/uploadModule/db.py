from abc import ABC,abstractmethod
from typing import List, Dict, Any

class db(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def upload_files(self,files: List[str], metadata: Dict[str,Any], db_route: str):
        pass
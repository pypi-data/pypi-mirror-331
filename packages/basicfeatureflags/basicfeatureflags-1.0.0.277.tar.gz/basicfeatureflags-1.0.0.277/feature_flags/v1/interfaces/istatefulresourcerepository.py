from abc import ABC, abstractmethod
from typing import List

class IStatefulResourceRepositoryV1(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_feature_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_feature_state_by_name(self, feature_name: str) -> bool:
        pass

    @abstractmethod
    def get_feature_name_by_index(self, index: int) -> str:
        pass

    @abstractmethod
    def get_feature_count(self) -> int:
        pass
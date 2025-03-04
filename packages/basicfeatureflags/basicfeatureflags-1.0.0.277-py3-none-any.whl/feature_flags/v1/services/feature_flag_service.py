from typing import List
from feature_flags.v1.interfaces.istatefulresourcerepository import IStatefulResourceRepositoryV1
from feature_flags.v1.repositories.basic_feature_repository import BasicFeatureRepositoryV1


class FeatureFlagServiceV1(IStatefulResourceRepositoryV1):

    def __init__(self, repository: IStatefulResourceRepositoryV1 = BasicFeatureRepositoryV1()):
        self.repository = repository

    def is_enabled(self, feature_name: str):
        return self.repository.get_feature_state_by_name(feature_name)
    
    # region IStatefulResourceRepositoryV1
    def get_feature_names(self) -> List[str]:
        return self.repository.get_feature_names()

    def get_feature_state_by_name(self, feature_name: str) -> bool:
        return self.repository.get_feature_state_by_name(feature_name)

    def get_feature_name_by_index(self, index: int) -> str:
        return self.repository.get_feature_name_by_index(index)

    def get_feature_count(self) -> int:
        return self.repository.get_feature_count()
    # endregion 

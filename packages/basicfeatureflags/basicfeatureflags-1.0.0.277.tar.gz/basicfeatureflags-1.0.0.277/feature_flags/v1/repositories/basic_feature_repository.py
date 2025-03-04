from typing import List
from feature_flags.v1.interfaces.istatefulresourcerepository import IStatefulResourceRepositoryV1
from feature_flags.v1.strategies.using_basic_flat_file import UsingBasicFlatFileV1

class BasicFeatureRepositoryV1(IStatefulResourceRepositoryV1):

    def __init__(self, strategy: UsingBasicFlatFileV1 = UsingBasicFlatFileV1()):
        self.strategy = strategy

    # region IStatefulResourceRepositoryV1
    def get_feature_names(self) -> List[str]:
        features_dictionary = self.strategy._read_resources_from_file()
        return list(features_dictionary.keys())
    
    def get_feature_state_by_name(self, feature_name: str) -> bool:
        features_dictionary = self.strategy._read_resources_from_file()
        try:
            is_enabled = features_dictionary[feature_name]
            return is_enabled
        except Exception as e:
            print(F"Could not find feature '{feature_name}'")
            return False

    def get_feature_name_by_index(self, index: int) -> str:
        features_dictionary = self.strategy._read_resources_from_file()
        list_of_feature_names = list(features_dictionary.keys())
        feature_name = list_of_feature_names[index]
        return feature_name

    def get_feature_count(self) -> int:
        features_dictionary = self.strategy._read_resources_from_file()
        count = len(features_dictionary)
        return count
    # endregion

'''
Usage:

from feature_flags import feature_flags

if feature_flags.is_enabled('feature_x'):
    print('Execute feature')
'''

from feature_flags.v1.services.feature_flag_service import FeatureFlagServiceV1
from feature_flags.v1.repositories.basic_feature_repository import BasicFeatureRepositoryV1
from feature_flags.v1.strategies.using_basic_flat_file import UsingBasicFlatFileV1

feature_flags = FeatureFlagServiceV1(
            repository=BasicFeatureRepositoryV1(
                strategy=UsingBasicFlatFileV1()))
import pytest
from moviepy.utils import close_all_clips

# @pytest.fixture(autouse=True, scope='function')
# def clean_between_tests():
#     yield
#     close_all_clips(scope='global')
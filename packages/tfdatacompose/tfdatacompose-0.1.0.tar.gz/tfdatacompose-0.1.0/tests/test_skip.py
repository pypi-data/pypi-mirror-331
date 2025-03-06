from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.skip import Skip


class TestSkip:
    def test_skip(self):
        dataset = Dataset.from_tensor_slices(arange(100))

        result = Skip(20)(dataset)

        expected = list(arange(20, 100))
        result = list(result.as_numpy_iterator())
        assert result == expected

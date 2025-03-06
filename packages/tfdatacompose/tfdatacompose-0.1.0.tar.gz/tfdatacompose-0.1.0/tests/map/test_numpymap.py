from numpy import arange
from tensorflow import int64
from tensorflow.python.data import Dataset

from tfdatacompose.map.numpymap import NumpyMap


class Double(NumpyMap):
    def map(self, number: int) -> int:
        return number * 2


class TestNumpyMap:
    def test_map(self):
        number_dataset = Dataset.from_tensor_slices(range(100))

        result = Double(int64)(number_dataset)

        expected = list(arange(100) * 2)
        result = list(result.as_numpy_iterator())
        assert result == expected

from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.map.map import Map


class Double(Map):
    def map(self, number: int) -> int:
        return number * 2


class TestMap:
    def test_map(self):
        number_dataset = Dataset.from_tensor_slices(range(100))

        result = Double()(number_dataset)

        expected = list(arange(100) * 2)
        result = list(result.as_numpy_iterator())
        assert result == expected

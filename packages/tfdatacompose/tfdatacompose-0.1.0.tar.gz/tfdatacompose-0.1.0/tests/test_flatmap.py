from numpy import arange
from tensorflow import Tensor
from tensorflow.python.data import Dataset

from tfdatacompose.flatmap import FlatMap


class Double(FlatMap):
    def flatmap(self, number: Tensor) -> Dataset:
        return Dataset.from_tensor_slices(number * 2)


class TestFlatMap:
    def test_flatmap(self):
        number_dataset = Dataset.from_tensor_slices(arange(100).reshape(20, 5))
        double_flatmap = Double()

        result = double_flatmap(number_dataset)

        result = list(result.as_numpy_iterator())
        expected = list(arange(100) * 2)
        assert result == expected

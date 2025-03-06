from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.filter.numpyfilter import NumpyFilter


class RemoveOdd(NumpyFilter):
    def filter(self, number: int) -> bool:
        return number % 2 == 0


class TestNumpyFilter:
    def test_filter(self):
        number_dataset = Dataset.from_tensor_slices(arange(100))
        filter_remove_odd = RemoveOdd()

        result = filter_remove_odd(number_dataset)

        result = list(result.as_numpy_iterator())
        expected = arange(100)
        expected = list(expected[expected % 2 == 0])
        assert result == expected

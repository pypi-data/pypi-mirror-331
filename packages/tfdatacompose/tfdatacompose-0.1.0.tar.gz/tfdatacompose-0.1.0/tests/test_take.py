from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.take import Take


class TestTake:
    def test_take(self):
        dataset = Dataset.from_tensor_slices(arange(100))

        result = Take(20)(dataset)

        result = list(result.as_numpy_iterator())
        expected = list(arange(20))
        assert result == expected

from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.lambdamap.lambdamap import LambdaMap


class TestLambdaMap:
    def test_lambdamap(self):
        number_dataset = Dataset.from_tensor_slices(range(100))

        result = LambdaMap(lambda x: x * 2)(number_dataset)

        expected = list(arange(100) * 2)
        result = list(result.as_numpy_iterator())
        assert result == expected

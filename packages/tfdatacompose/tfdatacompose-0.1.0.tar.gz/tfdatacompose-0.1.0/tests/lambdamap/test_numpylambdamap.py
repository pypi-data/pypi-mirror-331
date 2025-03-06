from numpy.core._multiarray_umath import arange
from tensorflow import int64
from tensorflow.python.data import Dataset

from tfdatacompose.lambdamap.numpylambdamap import NumpyLambdaMap


class TestNumpyLambdaMap:
    def test_lambdamap(self):
        number_dataset = Dataset.from_tensor_slices(range(100))

        result = NumpyLambdaMap(int64, lambda x: x * 2)(number_dataset)

        expected = list(arange(100) * 2)
        result = list(result.as_numpy_iterator())
        assert result == expected

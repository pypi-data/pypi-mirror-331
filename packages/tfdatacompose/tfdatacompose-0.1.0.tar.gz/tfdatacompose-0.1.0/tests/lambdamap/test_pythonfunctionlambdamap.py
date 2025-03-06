from numpy.core._multiarray_umath import arange
from tensorflow import int32
from tensorflow.python.data import Dataset

from tfdatacompose.lambdamap.pythonfunctionlambdamap import PythonFunctionLambdaMap


class TestPythonFunctionLambdaMap:
    def test_lamdbamap(self):
        number_dataset = Dataset.from_tensor_slices(range(100))

        result = PythonFunctionLambdaMap(int32, lambda x: x * 2)(number_dataset)

        expected = list(arange(100) * 2)
        result = list(result.as_numpy_iterator())
        assert result == expected

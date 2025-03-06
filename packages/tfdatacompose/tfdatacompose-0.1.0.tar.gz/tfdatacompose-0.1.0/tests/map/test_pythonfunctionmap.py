from numpy import arange
from tensorflow import int32
from tensorflow.python.data import Dataset

from tfdatacompose.map.pythonfunctionmap import PythonFunctionMap


class Double(PythonFunctionMap):
    def map(self, number: int) -> int:
        return number * 2


class TestPythonFunctionMap:
    def test_map(self):
        number_dataset = Dataset.from_tensor_slices(range(100))

        result = Double(int32)(number_dataset)

        expected = list(arange(100) * 2)
        result = list(result.as_numpy_iterator())
        assert result == expected

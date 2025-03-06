from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.util.print import Print


class TestPrint:
    def test_print(self):
        dataset = Dataset.from_tensor_slices(arange(10))

        result = Print()(dataset)
        for _ in result:
            pass  # Force Tensorflow to iterate through the dataset

        # TODO find a way to capture the Tensorflow output

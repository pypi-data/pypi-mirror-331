from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.util.printshape import PrintShape


class TestPrintShape:
    def test_printshape(self):
        dataset = Dataset.from_tensor_slices(arange(100).reshape((10, 2, 5)))

        result = PrintShape()(dataset)
        for _ in result:
            pass  # Force Tensorflow to iterate through the dataset

        # TODO find a way to capture the Tensorflow output

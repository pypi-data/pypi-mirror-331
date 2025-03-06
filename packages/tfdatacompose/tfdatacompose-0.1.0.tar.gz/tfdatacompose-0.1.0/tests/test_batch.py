from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.batch import Batch


class TestBatch:
    def test_batch(self):
        dataset = Dataset.from_tensor_slices(arange(100))

        result = Batch(5, False)(dataset)

        result = list(result.as_numpy_iterator())
        expected = list(arange(100).reshape((-1, 5)))
        for r, e in zip(result, expected):
            assert (r == e).all()

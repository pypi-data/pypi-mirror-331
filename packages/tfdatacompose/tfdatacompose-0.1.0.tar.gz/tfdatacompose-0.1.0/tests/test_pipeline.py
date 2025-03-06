from numpy import arange
from tensorflow.python.data import Dataset

from tfdatacompose.filter.filter import Filter
from tfdatacompose.map.map import Map
from tfdatacompose.pipeline import Pipeline


class Double(Map):
    def map(self, number: int) -> int:
        return number * 2


class RemoveOdd(Filter):
    def filter(self, number: int) -> bool:
        return number % 2 == 0


class TestPipeline:
    def test_pipeline(self):
        dataset = Dataset.from_tensor_slices(arange(100))
        pipeline = Pipeline(
            [
                RemoveOdd(),
                Double(),
            ]
        )

        result = pipeline(dataset)

        result = list(result.as_numpy_iterator())
        expected = arange(100)
        expected = list(expected[expected % 2 == 0] * 2)
        assert result == expected
